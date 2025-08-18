/**
 * Django jqGrid CSRF Token Setup
 * 
 * This file configures jQuery AJAX to automatically include Django's CSRF token
 * in all AJAX requests, eliminating the need for manual token handling.
 */

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Function to get CSRF token from cookie
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        // Function to check if URL is same origin
        function sameOrigin(url) {
            // URL could be relative or scheme relative or absolute
            const host = document.location.host; // host + port
            const protocol = document.location.protocol;
            const sr_origin = '//' + host;
            const origin = protocol + sr_origin;
            
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        
        // Configure jQuery AJAX to include CSRF token
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                // Only send the token to relative URLs i.e. locally.
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) && sameOrigin(settings.url)) {
                    // Try to get CSRF token from cookie first
                    let csrftoken = getCookie('csrftoken');
                    
                    // If not in cookie, try to get from meta tag
                    if (!csrftoken) {
                        csrftoken = $('meta[name="csrf-token"]').attr('content');
                    }
                    
                    // If not in meta tag, try to get from hidden input
                    if (!csrftoken) {
                        csrftoken = $('[name=csrfmiddlewaretoken]').val();
                    }
                    
                    // Set the token in request header
                    if (csrftoken) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            }
        });
        
        // Also set up traditional jQuery parameter serialization for jqGrid compatibility
        $.ajaxSetup({
            traditional: true
        });
    });
})(jQuery);