

function populatePost() {
    $.get("get-posts").done(function(data) {
          // console.log(data);
          // console.log(data['max_time']);
          var all_posts = $("#all-posts");
          all_posts.data('max_time', data['max_time']);
          all_posts.html('');
          for (var i = 0; i < data.messages.length; i++) {
              message = data.messages[i];
              all_posts.append(postHTML(message, data['user']));
          }
          $(".comment-button").click(showComments);
          $('.comment-form').each(inputNotEmpty);
          $('.comment-form').on('submit', submit);
      });
}

function getUpdates() {
    var all_posts = $("#all-posts")
    var max_time = all_posts.data('max_time');
    // console.log(max_time);
    $.get("update/" + max_time).done(function(data) {
        all_posts.data('max_time', data['max_time']);
        for (var i = 0; i < data.messages.length; i++) {
            var message = data.messages[i];
            all_posts.prepend(postHTML(message, data['user']));
        }
        if (data.messages.length > 0) {
              $(".comment-button").click(showComments);
              $('.comment-form').each(inputNotEmpty);
              $('.comment-form').on('submit', submit);
        }
    });
}


function postHTML(message, user) {
    var html =
        "<div id='post- " + message.id + "'>" +
              "<div class='container'>" +
                  "<p class='posthead'>" +
                      "<a href='/grumblr/home/" + message.username + "'>" +
                          "<img src='/grumblr/photo/"+ message.username +"' class='user-round'>" +
                      "</a>" +
                      "<a class='btn delete' href='/grumblr/add_fav/" + message.id + "'>" +
                          "<i class='far fa-star' title='Add to your favorite'></i>" +
                      "</a>" +
                      "<a class='text-body' href='/grumblr/home/" + message.username + "'>" +
                          "<b>" + message.username + "</b>" +
                      "<a/><br>" +
                      "<i class='time'>" + message.time + "</i><br>" +
                  "</p>" +
                  "<p>" + message.content +
                      "<btn class='btn btn-link float-right'><i class='far fa-comment-alt comment-button' id='button"+message.id+"'></i></btn>" +
                  "</p>" +
                  "<div class='container comment' id='show-comment"+message.id+"'>" +
                      "<form class='pt-3 pb-1 comment-form' id='comment-form-"+message.id+"'>" +
                          "<div class='form-row'>" +
                              "<div class='col-sm-1'>" +
                                  "<img class='comment-photo' src='/grumblr/photo/"+ user +"'>" +
                              "</div>" +
                              "<div class='col-sm-10'>" +
                                  "<input type='text' name='comment' class='form-control'>" +
                              "</div>" +
                              "<div class='col-sm-1'>" +
                                  "<button type='submit' class='btn btn-primary' disabled>-></button>" +
                              "</div>" +
                          "</div>" +
                      "</form>" +
                      "<hr>" +
                      "<div id='comments-"+message.id+"'></div>" +
                  "</div>" +

              "</div><hr>" +
          "</div>";
    return html;
}

$(function() {
    console.log("OK1");
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
    });

    populatePost();

    window.setInterval(getUpdates, 5000);
});