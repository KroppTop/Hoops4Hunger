<?php
/**
 * Hoops for Hunger team registration handler.
 *
 * 1. Validates the registration form.
 * 2. Adds the team captain to Hostinger Reach as a contact (subscriber).
 * 3. Emails the registration to the organizers.
 *
 * Settings (Reach API token, email addresses) live in a private config file,
 * never in this repository. See api/config.sample.php.
 */

declare(strict_types=1);

date_default_timezone_set('America/Chicago'); // Berlin, WI

// ---------- Config ----------
$configPaths = [
    __DIR__ . '/../../h4h-config.php', // preferred: one level above public_html, not web-accessible
    __DIR__ . '/config.php',           // fallback: next to this file (blocked by api/.htaccess)
];
$config = [];
foreach ($configPaths as $path) {
    if (is_file($path)) {
        $config = require $path;
        break;
    }
}
$config += [
    'reach_api_token' => getenv('REACH_API_TOKEN') ?: '',
    'reach_api_base'  => 'https://developers.hostinger.com',
    // "St. John Hoops for Hunger" Reach profile. The account has several profiles,
    // so contacts must be created on this one explicitly.
    'reach_profile_uuid' => 'b3101000-7629-4148-9e5e-be8e5885cb48',
    'reach_tag_uuids' => [],
    'notify_to'       => 'hello@hoops4hunger.com',
    'mail_from'       => 'hello@hoops4hunger.com',
    'mail_from_name'  => 'Hoops for Hunger Website',
];

// ---------- Helpers ----------
$wantsJson = (($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') === 'fetch')
    || str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');

function respond(bool $ok, string $message, int $status = 200, array $extra = []): never
{
    global $wantsJson;
    if ($wantsJson) {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
        echo json_encode(['ok' => $ok, 'message' => $message] + $extra);
    } else {
        // Plain HTML form post (JavaScript disabled): send them back to the page.
        $q = $ok ? 'status=ok' : 'status=error&msg=' . rawurlencode($message);
        header('Location: ../register.html?' . $q . '#registration-form', true, 303);
    }
    exit;
}

function field(string $name, int $max): string
{
    $v = trim((string)($_POST[$name] ?? ''));
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v) ?? '';
    return mb_substr($v, 0, $max);
}

function oneLine(string $v): string
{
    return trim(preg_replace('/[\r\n]+/', ' ', $v) ?? '');
}

/** Convert a phone number to E.164 (+15551234567). Assumes US/Canada for 10-digit numbers. */
function toE164(string $phone): ?string
{
    $hasPlus = str_starts_with(trim($phone), '+');
    $digits = preg_replace('/\D+/', '', $phone) ?? '';
    if (!$hasPlus && strlen($digits) === 10) return '+1' . $digits;
    if (!$hasPlus && strlen($digits) === 11 && $digits[0] === '1') return '+' . $digits;
    if ($hasPlus && strlen($digits) >= 7 && strlen($digits) <= 15) return '+' . $digits;
    return null;
}

function addToReach(array $config, array $contact): array
{
    // Forgive common paste mistakes: surrounding whitespace/quotes or a "Bearer " prefix.
    $token = trim((string)$config['reach_api_token'], " \t\n\r\0\x0B\"'");
    $token = preg_replace('/^Bearer\s+/i', '', $token) ?? $token;
    if ($token === '' || str_starts_with($token, 'PASTE-YOUR')) {
        return [false, 'Reach API token is not configured'];
    }
    $base = rtrim($config['reach_api_base'], '/');
    $url = $config['reach_profile_uuid'] !== ''
        ? $base . '/api/reach/v1/profiles/' . rawurlencode($config['reach_profile_uuid']) . '/contacts'
        : $base . '/api/reach/v1/contacts';
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 15,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $token,
            'Content-Type: application/json',
            'Accept: application/json',
        ],
        CURLOPT_POSTFIELDS     => json_encode($contact),
    ]);
    $body = curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $err  = curl_error($ch);
    curl_close($ch);

    if ($body === false) {
        return [false, 'Could not reach Hostinger: ' . $err];
    }
    if ($code >= 200 && $code < 300) {
        return [true, 'Added to Hostinger Reach'];
    }
    $detail = '';
    $json = json_decode((string)$body, true);
    if (is_array($json)) {
        $detail = (string)($json['message'] ?? $json['error'] ?? '');
    }
    return [false, "Hostinger Reach returned HTTP $code" . ($detail !== '' ? ": $detail" : '')];
}

// ---------- Request checks ----------
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    respond(false, 'Please submit the registration form.', 405);
}

// Spam trap: real people never see or fill this field.
if (field('website', 200) !== '') {
    respond(true, 'Thanks! Your registration has been received.');
}

$team    = oneLine(field('team', 80));
$captain = oneLine(field('captain', 80));
$email   = oneLine(field('email', 160));
$phone   = oneLine(field('phone', 40));
$heights = str_replace(["\r\n", "\r"], "\n", field('heights', 600));

$missing = [];
if ($team === '')    $missing[] = 'Team Name';
if ($captain === '') $missing[] = "Captain's Name";
if ($email === '')   $missing[] = 'Email Address';
if ($phone === '')   $missing[] = 'Phone Number';
if ($missing) {
    respond(false, 'Please fill in: ' . implode(', ', $missing) . '.', 422);
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(false, 'Please enter a valid email address.', 422);
}
if (strlen(preg_replace('/\D+/', '', $phone) ?? '') < 7) {
    respond(false, 'Please enter a valid phone number.', 422);
}

// ---------- 1. Add captain to Hostinger Reach ----------
$nameParts = preg_split('/\s+/', $captain, 2) ?: [$captain];
$e164 = toE164($phone);
// Reach limits the note to 75 characters; heights and the rest go in the email.
$note = mb_substr("Hoops for Hunger team: $team", 0, 75);

$contact = array_filter([
    'email'     => $email,
    'name'      => $nameParts[0],
    'surname'   => $nameParts[1] ?? null,
    'phone'     => $e164,
    'note'      => $note,
    'tag_uuids' => $config['reach_tag_uuids'] ?: null,
], fn($v) => $v !== null && $v !== '');

[$reachOk, $reachMsg] = addToReach($config, $contact);
if (!$reachOk) {
    error_log('[hoops4hunger] Reach contact failed for ' . $email . ': ' . $reachMsg);
    // Private log next to this file (blocked from the web by api/.htaccess).
    // Records the error and the token's shape only, never the token itself.
    $raw = (string)$config['reach_api_token'];
    $shape = sprintf('token length %d, has whitespace: %s, has "Bearer": %s',
        strlen($raw), preg_match('/\s/', $raw) ? 'yes' : 'no', stripos($raw, 'bearer') !== false ? 'yes' : 'no');
    @file_put_contents(__DIR__ . '/reach-errors.log',
        date('c') . "  $reachMsg  ($shape)\n", FILE_APPEND | LOCK_EX);
}

// ---------- 2. Email the organizers ----------
$subject = 'New Team Registration: ' . $team;
$lines = [
    'A new team registered on hoops4hunger.com.',
    '',
    "Team Name:      $team",
    "Captain's Name: $captain",
    "Email Address:  $email",
    "Phone Number:   $phone",
    '',
    'Individual Player Heights:',
    $heights !== '' ? $heights : '(not provided)',
    '',
    'Hostinger Reach: ' . ($reachOk ? 'captain added as a contact' : 'NOT added (' . $reachMsg . '), please add them manually'),
    '',
    'Submitted: ' . date('l, F j, Y g:i A T'),
    'Reply to this email to reach the captain directly.',
];
$fromName = '=?UTF-8?B?' . base64_encode($config['mail_from_name']) . '?=';
$headers = [
    'From: ' . $fromName . ' <' . $config['mail_from'] . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: Hoops4Hunger-Website',
];
$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
$mailOk = @mail(
    $config['notify_to'],
    $encodedSubject,
    str_replace("\n", "\r\n", implode("\n", $lines)),
    implode("\r\n", $headers),
    '-f' . $config['mail_from']
);
if (!$mailOk) {
    error_log('[hoops4hunger] Notification email failed for team ' . $team);
}

// ---------- 3. Respond ----------
if (!$mailOk && !$reachOk) {
    respond(false, 'Sorry, we could not save your registration. Please email hello@hoops4hunger.com or call (920) 658-3029.', 500);
}
respond(true, "Thanks, $captain! $team is registered. Remember to bring one paper bag of nonperishable food to check-in.", 200, [
    'reach' => $reachOk,
    'email' => $mailOk,
]);
