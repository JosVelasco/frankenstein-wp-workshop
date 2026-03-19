#!/usr/bin/env python3
"""
Build blueprint.json for the Frankenstein WP Workshop.
Run after any change to mu-plugin.php to keep the inline copy current.
"""
import json

with open('mu-plugin.php', 'r') as f:
    mu_plugin_content = f.read()

# ── Checklist page PHP ────────────────────────────────────────────────────────
checklist_php = r"""<?php
require_once '/wordpress/wp-load.php';

$pid = wp_insert_post( array(
    'post_title'     => 'Workshop Checklist',
    'post_name'      => 'workshop-checklist',
    'post_status'    => 'publish',
    'post_type'      => 'page',
    'comment_status' => 'closed',
    'post_content'   => '',
) );

$c  = '<!-- wp:paragraph --><p>Work through each task below. Each one includes a discussion question to think about as you go. When you are done, take the quiz linked at the bottom of this page.</p><!-- /wp:paragraph -->';

$c .= '<!-- wp:heading --><h2 class="wp-block-heading">1. Plugin Audit</h2><!-- /wp:heading -->';
$c .= '<!-- wp:paragraph --><p>Two caching plugins (W3 Total Cache and WP Super Cache) and two SEO plugins (Yoast SEO and All in One SEO) are active at the same time. Deactivate and delete the duplicates. Also remove Hello Dolly, WP Post Ratings, and any unused page builder.</p><!-- /wp:paragraph -->';
$c .= '<!-- wp:paragraph --><p><strong>Discussion:</strong> Why is running two caching plugins at once a problem? What happens when both try to serve a page?</p><!-- /wp:paragraph -->';

$c .= '<!-- wp:heading --><h2 class="wp-block-heading">2. Theme Cleanup</h2><!-- /wp:heading -->';
$c .= '<!-- wp:paragraph --><p>Four themes are installed but only one is active. Delete the unused ones from Appearance &gt; Themes.</p><!-- /wp:paragraph -->';
$c .= '<!-- wp:paragraph --><p><strong>Discussion:</strong> Each inactive theme is an attack surface. Why? What kind of vulnerabilities do unused themes introduce?</p><!-- /wp:paragraph -->';

$c .= '<!-- wp:heading --><h2 class="wp-block-heading">3. Performance Fixes</h2><!-- /wp:heading -->';
$c .= '<!-- wp:paragraph --><p>Contact Form 7 and Smart Slider 3 load CSS and JavaScript on every page, even where they are not used. Open Query Monitor and check the Scripts and Styles tab to confirm.</p><!-- /wp:paragraph -->';
$c .= '<!-- wp:paragraph --><p><strong>Discussion:</strong> How would you prevent a plugin from loading its assets globally? Is there a setting in the plugin, or does it need to be handled in code?</p><!-- /wp:paragraph -->';

$c .= '<!-- wp:heading --><h2 class="wp-block-heading">4. Database Cleanup</h2><!-- /wp:heading -->';
$c .= '<!-- wp:paragraph --><p>There are 100 auto-generated comments, 50 auto-generated posts, and 10 revisions on a single post. Install a plugin like WP-Sweep or Advanced DB Cleaner to find and remove them.</p><!-- /wp:paragraph -->';
$c .= '<!-- wp:paragraph --><p><strong>Discussion:</strong> Check the autoloaded options in wp_options. Which ones look suspicious? What is the risk of a bloated autoload?</p><!-- /wp:paragraph -->';

$c .= '<!-- wp:heading --><h2 class="wp-block-heading">5. Mystery Code</h2><!-- /wp:heading -->';
$c .= '<!-- wp:paragraph --><p>There is a must-use plugin that cannot be deactivated from the Plugins screen. Find it under Plugins &gt; Must-Use Plugins. Use Tools &gt; File Editor to open wp-content/mu-plugins/custom-tweaks.php and read the code.</p><!-- /wp:paragraph -->';
$c .= '<!-- wp:paragraph --><p><strong>Discussion:</strong> Identify at least 3 things it does that hurt performance or break the site. What would you do with this file on a real production site?</p><!-- /wp:paragraph -->';

$c .= '<!-- wp:heading --><h2 class="wp-block-heading">Your Conclusions</h2><!-- /wp:heading -->';
$c .= '<!-- wp:paragraph --><p>Write your notes here. What did you find? What surprised you most? Take a screenshot to share with the group.</p><!-- /wp:paragraph -->';

wp_update_post( array( 'ID' => $pid, 'post_content' => $c ) );
"""

# ── Quiz creation PHP ─────────────────────────────────────────────────────────
quiz_php = r"""<?php
require_once '/wordpress/wp-load.php';

global $wpdb;

$wpdb->insert( $wpdb->prefix . 'mlw_quizzes', array(
    'quiz_name'          => 'Frankenstein WP: Knowledge Check',
    'randomness_order'   => 2,
    'show_score'         => 1,
    'total_user_tries'   => 0,
    'ajax_show_correct'  => 1,
    'require_log_in'     => 0,
    'user_name'          => 2,
    'user_comp'          => 2,
    'user_email'         => 2,
    'user_phone'         => 2,
    'comment_section'    => 1,
    'deleted'            => 0,
    'quiz_views'         => 0,
    'quiz_taken'         => 0,
    'last_activity'      => current_time( 'mysql' ),
    'submit_button_text' => '',
    'message_before'     => '',
    'message_after'      => '',
) );
$quiz_id = $wpdb->insert_id;

function fw_q( $quiz_id, $text, $answers, $correct_idx ) {
    global $wpdb;
    $arr = array();
    foreach ( $answers as $i => $a ) {
        $arr[] = array( $a, ( $i === $correct_idx ) ? 1 : 0, ( $i === $correct_idx ) ? 1 : 0, '' );
    }
    $wpdb->insert( $wpdb->prefix . 'mlw_questions', array(
        'quiz_id'               => $quiz_id,
        'question_name'         => $text,
        'answer_array'          => maybe_serialize( $arr ),
        'correct_answer'        => $correct_idx + 1,
        'question_type'         => 0,
        'question_type_new'     => '0',
        'question_order'        => 0,
        'comments'              => 1,
        'question_settings'     => maybe_serialize( array( 'Required' => '0' ) ),
        'deleted'               => 0,
        'deleted_question_bank' => 0,
    ) );
    return $wpdb->insert_id;
}

$qids = array();

$qids[] = fw_q( $quiz_id,
    'What is the main risk of having two caching plugins active at the same time?',
    array(
        'Higher memory usage but faster page loads',
        'They can serve conflicting cached versions of pages, causing errors and broken output',
        'WordPress automatically disables one of them to prevent conflicts',
        'The site loads slower because both plugins run simultaneously',
    ),
    1
);

$qids[] = fw_q( $quiz_id,
    'Why are inactive (unused) themes considered a security risk?',
    array(
        'They increase the size of the WordPress database over time',
        'They slow down the admin dashboard significantly',
        'They can contain unpatched vulnerabilities that attackers can exploit, even when not active',
        'WordPress cannot automatically update inactive themes',
    ),
    2
);

$qids[] = fw_q( $quiz_id,
    'Which tool in this workshop environment lets you see which scripts and styles are loading on a given page?',
    array(
        'Yoast SEO',
        'W3 Total Cache',
        'Query Monitor',
        'Akismet',
    ),
    2
);

$qids[] = fw_q( $quiz_id,
    'What does the posts_where filter in custom-tweaks.php silently do?',
    array(
        'Caches all post database queries to improve performance',
        'Shows only posts published by the admin user',
        'Hides all posts with a modified date before 2010',
        'Randomises the order of posts on the front page',
    ),
    2
);

$qids[] = fw_q( $quiz_id,
    'Which statement is TRUE about must-use plugins?',
    array(
        'They appear in the Plugins screen and can be deactivated like any other plugin',
        'They are installed from the WordPress.org plugin directory',
        'They load automatically on every request and cannot be deactivated from the admin UI',
        'They require a paid WordPress.com account',
    ),
    2
);

$qids[] = fw_q( $quiz_id,
    'What is the performance problem with the thumbnail regeneration code in custom-tweaks.php?',
    array(
        'It converts all uploaded images to PNG format on every save',
        'It runs on every page load and updates attachment metadata for every image in the library',
        'It deletes duplicate thumbnails from the media library on activation',
        'It regenerates thumbnails only when the source image is missing',
    ),
    1
);

$qids[] = fw_q( $quiz_id,
    'The mu-plugin reroutes all outgoing email to noreply@localhost. What is the most likely impact on a live site?',
    array(
        'The site sends emails faster because localhost delivery is instant',
        'Admin notification emails are duplicated to the localhost address',
        'All transactional emails (password resets, order confirmations) are silently lost',
        'WordPress automatically falls back to a working mail address',
    ),
    2
);

$qids[] = fw_q( $quiz_id,
    'Why is using ini_set(\'memory_limit\', \'1024M\') inside a plugin considered bad practice?',
    array(
        'PHP does not allow ini_set to change the memory limit at runtime',
        'WordPress overrides it with its own memory limit setting',
        'It masks the root cause of memory problems rather than fixing them',
        'It only applies to the admin area, not the public-facing site',
    ),
    2
);

// Link questions to quiz via pages structure (QSM uses this for its IN() query)
$wpdb->update(
    $wpdb->prefix . 'mlw_quizzes',
    array( 'quiz_settings' => maybe_serialize( array(
        'pages'                  => array( $qids ),
        'enable_quick_result_mc' => 1,
    ) ) ),
    array( 'quiz_id' => $quiz_id )
);

// Create published qsm_quiz post (required so QSM does not show a draft warning)
$quiz_post_id = wp_insert_post( array(
    'post_title'   => 'Frankenstein WP: Knowledge Check',
    'post_content' => '[mlw_quizmaster quiz=' . $quiz_id . ']',
    'post_status'  => 'publish',
    'post_author'  => get_current_user_id(),
    'post_type'    => 'qsm_quiz',
) );
add_post_meta( $quiz_post_id, 'quiz_id', intval( $quiz_id ) );

// Create the publicly accessible quiz page (regular page, not qsm_quiz CPT)
$kid = wp_insert_post( array(
    'post_title'  => 'Knowledge Check',
    'post_name'   => 'knowledge-check',
    'post_status' => 'publish',
    'post_type'   => 'page',
    'post_content' => '',
) );
$shortcode = '[mlw_quizmaster quiz=' . $quiz_id . ']';
$k  = '<!-- wp:paragraph --><p>Eight questions, one from each area of the workshop. Click an answer to see immediately whether you were right.</p><!-- /wp:paragraph -->';
$k .= '<!-- wp:shortcode -->' . $shortcode . '<!-- /wp:shortcode -->';
wp_update_post( array( 'ID' => $kid, 'post_content' => $k ) );

// Append Knowledge Check link and conclusions to the checklist page
$checklist = get_page_by_path( 'workshop-checklist' );
if ( $checklist ) {
    $quiz_url = get_permalink( $kid );
    $q  = '<!-- wp:separator --><hr class="wp-block-separator has-alpha-channel-opacity"/><!-- /wp:separator -->';
    $q .= '<!-- wp:heading {"level":2} --><h2 class="wp-block-heading">Knowledge Check</h2><!-- /wp:heading -->';
    $q .= '<!-- wp:paragraph --><p>Finished all five tasks? Head to the <a href="' . $quiz_url . '">Knowledge Check</a> to confirm what you have learned.</p><!-- /wp:paragraph -->';
    wp_update_post( array( 'ID' => $checklist->ID, 'post_content' => $checklist->post_content . $q ) );
}

echo 'quiz done';
"""

# ── Blueprint structure ───────────────────────────────────────────────────────
blueprint = {
    "$schema": "https://playground.wordpress.net/blueprint-schema.json",
    "landingPage": "/wp-admin",
    "login": True,
    "preferredVersions": {
        "wp": "6.9",
        "php": "8.2"
    },
    "steps": [
        # 1. Create checklist page
        {
            "step": "runPHP",
            "code": checklist_php
        },
        # 2. Themes
        {
            "step": "installTheme",
            "themeData": {"resource": "wordpress.org/themes", "slug": "twentyfifteen"},
            "options": {"activate": True}
        },
        {
            "step": "installTheme",
            "themeData": {"resource": "wordpress.org/themes", "slug": "twentyseventeen"}
        },
        {
            "step": "installTheme",
            "themeData": {"resource": "wordpress.org/themes", "slug": "astra"}
        },
        {
            "step": "installTheme",
            "themeData": {"resource": "wordpress.org/themes", "slug": "oceanwp"}
        },
        # 3. Suppress AIOSEO splash before install
        {
            "step": "wp-cli",
            "command": "wp option add aioseop_options '{\"placeholder\":true}' --allow-root"
        },
        # 4. Plugins
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "beaver-builder-lite-version"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "w3-total-cache"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "wp-super-cache"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "wordpress-seo"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "all-in-one-seo-pack"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "smart-slider-3"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "contact-form-7"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "broken-link-checker"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "regenerate-thumbnails"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "akismet"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "hello-dolly"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "wp-postratings"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "query-monitor"}
        },
        {
            "step": "installPlugin",
            "pluginData": {"resource": "wordpress.org/plugins", "slug": "quiz-master-next"}
        },
        # 5. Download demo image first, then import it
        {
            "step": "writeFile",
            "path": "/wordpress/wp-content/demo-image.jpg",
            "data": {
                "resource": "url",
                "url": "https://picsum.photos/seed/haunted/2000/1333"
            }
        },
        {
            "step": "wp-cli",
            "command": "wp media import /wordpress/wp-content/demo-image.jpg --title='Demo Large Image' --allow-root"
        },
        {
            "step": "wp-cli",
            "command": "wp post generate --count=50 --post_status=publish --allow-root"
        },
        {
            "step": "wp-cli",
            "command": "wp comment generate --count=100 --allow-root"
        },
        {
            "step": "wp-cli",
            "command": "wp post create --post_title='About Us' --post_status=publish --post_type=page --post_content='[vc_row][vc_column width=\"1/2\"][vc_column_text]Welcome to our company. We have been in business for many years.[/vc_column_text][/vc_column][vc_column width=\"1/2\"][vc_single_image image=\"1\" img_size=\"full\"][/vc_column][/vc_row][vc_row][vc_column][vc_btn title=\"Contact Us\" style=\"3d\" color=\"danger\" size=\"lg\" align=\"center\"][/vc_column][/vc_row]' --allow-root"
        },
        {
            "step": "wp-cli",
            "command": "wp post create --post_title='Services' --post_status=publish --post_type=page --post_content='<!-- wp:paragraph --><p>Our services include the following:</p><!-- /wp:paragraph -->[et_pb_section][et_pb_row][et_pb_column type=\"4_4\"][et_pb_text]These are our services. Please call us.[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]<div style=\"color:red;font-size:24px;font-weight:bold\">UNDER CONSTRUCTION - DO NOT DELETE</div>' --allow-root"
        },
        # 10 revisions on post 1
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 1' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 2' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 3' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 4' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 5' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 6' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 7' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 8' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 9' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Revision 10' --allow-root"},
        {"step": "wp-cli", "command": "wp post update 1 --post_content='Welcome to our site! Check out our services.' --allow-root"},
        {
            "step": "wp-cli",
            "command": "wp option update blogdescription 'Just another WordPress site' --allow-root"
        },
        {
            "step": "wp-cli",
            "command": "wp config set WP_DEBUG true --raw --allow-root"
        },
        {
            "step": "wp-cli",
            "command": "wp config set WP_DEBUG_LOG true --raw --allow-root"
        },
        {
            "step": "wp-cli",
            "command": "wp config set WP_DEBUG_DISPLAY false --raw --allow-root"
        },
        # 6. Banner image (from jsDelivr after repo is live)
        {
            "step": "writeFile",
            "path": "/wordpress/wp-content/uploads/frankenstein-wp-workshop.jpg",
            "data": {
                "resource": "url",
                "url": "https://cdn.jsdelivr.net/gh/JosVelasco/frankenstein-wp-workshop@main/images/frankenstein-wp-workshop.jpg"
            }
        },
        # 7. mu-plugins dir + inline plugin
        {
            "step": "mkdir",
            "path": "/wordpress/wp-content/mu-plugins"
        },
        {
            "step": "writeFile",
            "path": "/wordpress/wp-content/mu-plugins/custom-tweaks.php",
            "data": mu_plugin_content
        },
        # 8. Create quiz (must run after QSM plugin is installed)
        {
            "step": "runPHP",
            "code": quiz_php
        },
    ]
}

with open('blueprint.json', 'w') as f:
    json.dump(blueprint, f, indent=2, ensure_ascii=False)

print("blueprint.json written successfully.")
print(f"mu-plugin.php inlined: {len(mu_plugin_content)} chars")
