<?php
/**
 * Copy this file to ONE of these locations and fill in your values:
 *   - h4h-config.php in the folder ABOVE public_html (best: not reachable from the web)
 *   - api/config.php (also works; api/.htaccess blocks direct access)
 *
 * Never commit the real file: it contains your Hostinger API token.
 */
return [
    // Generate an API token in hPanel (see README: "Turning on the registration form")
    'reach_api_token' => 'PASTE-YOUR-HOSTINGER-API-TOKEN-HERE',

    // Optional: which Reach profile gets the contacts (defaults to St. John Hoops for Hunger).
    // 'reach_profile_uuid' => 'b3101000-7629-4148-9e5e-be8e5885cb48',

    // Optional: Reach tag UUIDs to attach to every registrant (e.g. a "2027 Teams" tag).
    'reach_tag_uuids' => [],

    // Where registration emails go, and who they come from.
    // mail_from should be a mailbox on this domain so the email is not marked as spam.
    'notify_to'      => 'hello@hoops4hunger.com',
    'mail_from'      => 'hello@hoops4hunger.com',
    'mail_from_name' => 'Hoops for Hunger Website',
];
