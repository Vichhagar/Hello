const go_to_post_detail = (post_body) => {
    let post_id = post_body.getAttribute('data-post-id')
    window.location.href = '/post/' + post_id + '/';
}

const go_to_activity_detail = (activity_body) => {
    let activity_id = activity_body.getAttribute('data-activity-id')
    window.location.href = '/activity/' + activity_id + '/';
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
}

const like_post = (id) => {
    $.ajax({
        url: `/post/${id}/like/`,
        type: 'POST',
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken')
        },
        success: function(response) {
            // Replace the contents of the post details div with the response HTML
            // $('#post-details').html(response);
            if(response.success) {
                window.location.reload();
            }
        },
        error: function(xhr) {
            // Handle errors here
            console.log(xhr)
        }
    });
}

const save_post = (id) => {
    $.ajax({
        url: `/post/${id}/save/`,
        type: 'POST',
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken')
        },
        success: function(response) {
            // Replace the contents of the post details div with the response HTML
            // $('#post-details').html(response);
            console.log(response)
            if(response.success) {
                window.location.reload();
            }
        },
        error: function(xhr) {
            // Handle errors here
            console.log(xhr)
        }
    });
}