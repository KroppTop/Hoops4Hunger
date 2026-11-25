<?php
/**
 * Registered team list, shared by register.php (adds teams) and teams.php (lists them).
 *
 * Stored in api/data/teams.json, which api/.htaccess blocks from direct web access.
 * Only team names are ever shown publicly. To remove or rename a team, edit
 * api/data/teams.json in hPanel's File Manager.
 */

declare(strict_types=1);

const TEAMS_FILE = __DIR__ . '/data/teams.json';

/** Teams that registered before the online form existed. Used to start the list. */
const TEAMS_SEED = ['Shrek', 'Team Perspiration', 'The Golden Girls', 'Triple Threat'];

/** Read the list: [['name' => ..., 'added' => ISO date], ...] in sign-up order. */
function teams_read(): array
{
    if (!is_file(TEAMS_FILE)) {
        return array_map(fn($n) => ['name' => $n, 'added' => null], TEAMS_SEED);
    }
    $data = json_decode((string)file_get_contents(TEAMS_FILE), true);
    return is_array($data['teams'] ?? null) ? $data['teams'] : [];
}

/** Add a team unless one with the same name (ignoring case and spacing) is already listed. */
function teams_add(string $name): bool
{
    $name = trim(preg_replace('/\s+/u', ' ', $name) ?? '');
    if ($name === '') return false;

    $dir = dirname(TEAMS_FILE);
    if (!is_dir($dir) && !@mkdir($dir, 0755, true)) return false;

    $fh = @fopen(TEAMS_FILE, 'c+');
    if (!$fh) return false;
    try {
        flock($fh, LOCK_EX);
        $raw = stream_get_contents($fh);
        $data = $raw !== '' ? json_decode((string)$raw, true) : null;
        $teams = is_array($data['teams'] ?? null)
            ? $data['teams']
            : array_map(fn($n) => ['name' => $n, 'added' => null], TEAMS_SEED);

        $key = mb_strtolower($name);
        foreach ($teams as $t) {
            if (mb_strtolower(trim((string)($t['name'] ?? ''))) === $key) {
                return false; // already listed
            }
        }
        $teams[] = ['name' => $name, 'added' => date('c')];

        ftruncate($fh, 0);
        rewind($fh);
        fwrite($fh, json_encode(['teams' => $teams], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
        fflush($fh);
        return true;
    } finally {
        flock($fh, LOCK_UN);
        fclose($fh);
    }
}
