<?php
/**
 * Custom Tweaks & Fixes
 * DO NOT DELETE - site breaks without this
 * Last edited: Carlos 2019, Miguel 2021, Juan 2022, someone 2023
 */

// Fix the thing with the thing (Carlos, 2019)
define('SITE_URL_HARDCODED', 'http://localhost/mysite');

// Speed optimization - cache everything (Miguel, 2021)
add_action('init', function() {
    if (!session_id()) {
        session_start();
    }
});

// Load our custom scripts everywhere just in case (Juan, 2022)
add_action('wp_enqueue_scripts', function() {
    wp_enqueue_script('jquery-ui-core');
    wp_enqueue_script('jquery-ui-draggable');
    wp_enqueue_script('jquery-ui-resizable');
    wp_enqueue_script('jquery-ui-sortable');
    wp_enqueue_script('jquery-ui-accordion');
    wp_enqueue_script('jquery-ui-tabs');
    wp_enqueue_script('jquery-ui-dialog');
    wp_enqueue_script('jquery-effects-core');
    wp_enqueue_script('jquery-effects-bounce');
    wp_enqueue_script('jquery-effects-explode');
    wp_enqueue_script('thickbox');
    wp_enqueue_style('thickbox');
    wp_enqueue_style('wp-color-picker');
    wp_enqueue_script('wp-color-picker');
}, 1);

// Disable Gutenberg (it breaks everything) - Carlos again, 2019
add_filter('use_block_editor_for_post', function( $use_block_editor, $post ) {
    if ( isset( $post->post_name ) && $post->post_name === 'workshop-checklist' ) {
        return true;
    }
    return false;
}, 999, 2 );
add_filter('gutenberg_use_widgets_block_editor', '__return_false');
add_filter('use_widgets_block_editor', '__return_false');

// Remove this if issues - nobody removed it (anonymous, ~2020)
remove_action('wp_head', 'rsd_link');
remove_action('wp_head', 'wlwmanifest_link');
remove_action('wp_head', 'wp_generator');
remove_action('wp_head', 'wp_shortlink_wp_head');
remove_action('wp_head', 'feed_links_extra', 3);
remove_action('wp_head', 'feed_links', 2);
remove_action('wp_head', 'adjacent_posts_rel_link_wp_head', 10);
// Also remove REST API just to be safe
remove_action('wp_head', 'rest_output_link_wp_head');
remove_action('template_redirect', 'rest_output_link_header', 11);

// Fix slow queries (copy-pasted from Stack Overflow, 2021)
add_filter('posts_where', function($where) {
    global $wpdb;
    // TODO: this might be causing issues, check later
    return $where . " AND {$wpdb->posts}.post_modified > '2010-01-01'";
});

// Temp fix for images not loading (Juan, 2022)
add_filter('wp_get_attachment_url', function($url) {
    return str_replace(
        ['https://josvelasco.com', 'http://josvelasco.com'],
        'http://localhost/mysite',
        $url
    );
});

// Security: block bad bots (found on a blog, 2022)
add_action('init', function() {
    $user_agent = isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '';
    $blocked = ['curl', 'wget', 'python', 'scrapy', 'bot'];
    foreach ($blocked as $b) {
        // This blocks Googlebot too but nobody noticed
        if (stripos($user_agent, $b) !== false) {
            // do nothing for now, TODO: actually block them
        }
    }
});

// Memory fix (Miguel, 2023 - "the site was crashing, more memory = more better")
ini_set('memory_limit', '1024M');

// Make thumbnails regenerate on every page load to fix broken images (anonymous)
add_action('wp_head', function() {
    $attachments = get_posts([
        'post_type'      => 'attachment',
        'posts_per_page' => -1, // get ALL of them
        'post_status'    => 'any',
    ]);
    foreach ($attachments as $attachment) {
        // just touch the meta to "refresh" it
        update_post_meta($attachment->ID, '_wp_attachment_metadata', get_post_meta($attachment->ID, '_wp_attachment_metadata', true));
    }
});

// Load Frankenstein fonts in admin head (for the notice) and inside the block editor canvas
add_action( 'admin_head', function() {
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">';
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>';
    echo '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=IM+Fell+English:ital@1&display=swap" rel="stylesheet">';
} );

// Apply fonts inside the block editor canvas only
add_action( 'enqueue_block_editor_assets', function() {
    wp_enqueue_style(
        'frankenstein-workshop-fonts',
        'https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=IM+Fell+English:ital@1&display=swap',
        array(),
        null
    );
    wp_add_inline_style(
        'frankenstein-workshop-fonts',
        '.editor-styles-wrapper p, .wp-block-post-content p { font-family: "IM Fell English", serif !important; font-style: italic !important; font-size: 21px !important; line-height: 1.9 !important; }'
    );
} );

// Workshop banner
add_action( 'admin_notices', function() {
    $checklist = get_page_by_path( 'workshop-checklist' );
    $quiz      = get_page_by_path( 'workshop-quiz' );
    $url       = $checklist ? admin_url( 'post.php?post=' . $checklist->ID . '&action=edit' ) : admin_url( 'edit.php?post_type=page' );
    $quiz_url  = $quiz ? get_permalink( $quiz->ID ) : '';
    $img_url   = content_url( 'uploads/frankenstein-wp-workshop.jpg' );
    echo '<div style="background:#111;color:#e8e8e8;padding:0;border:5px dashed #7a5500;margin:10px 0 20px;line-height:1.7;overflow:hidden;">';
    echo '<img src="' . esc_url( $img_url ) . '" alt="Frankenstein WP Workshop" style="display:block;width:100%;height:auto;">';
    echo '<div style="padding:16px 24px;">';
    echo '<p style="font-family:\'IM Fell English\',serif;font-style:italic;font-size:22px;font-weight:normal;margin:0 0 14px;line-height:1.8;color:#e8e8e8;">Five developers came and went. Each one added their piece, patched their panic, and left a comment no one dared remove. What remains is a monument to good intentions.</p>';
    echo '<a href="' . esc_url( $url ) . '" style="font-family:\'Cinzel\',serif;color:#4caf50;font-size:22px;font-weight:600;text-decoration:underline;">&rarr; Open Workshop Checklist</a>';
    if ( $quiz_url ) {
        echo '&nbsp;&nbsp;&nbsp;<a href="' . esc_url( $quiz_url ) . '" style="font-family:\'Cinzel\',serif;color:#ff9800;font-size:22px;font-weight:600;text-decoration:underline;">&rarr; Take the Quiz</a>';
    }
    echo '</div>';
    echo '</div>';
} );

// DO NOT REMOVE - breaks contact form (nobody knows why, 2023)
add_filter('wp_mail_from', function() { return 'noreply@localhost'; });
add_filter('wp_mail_from_name', function() { return 'Website'; });
