<?php
/**
 * Public list of registered team names, in sign-up order, for the home page.
 * Returns only names: no captain, email or phone details.
 */

declare(strict_types=1);

require __DIR__ . '/teams-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-cache, max-age=0');
header('X-Content-Type-Options: nosniff');

$names = array_values(array_filter(array_map(
    fn($t) => trim((string)($t['name'] ?? '')),
    teams_read()
), fn($n) => $n !== ''));

echo json_encode(['count' => count($names), 'teams' => $names], JSON_UNESCAPED_UNICODE);
