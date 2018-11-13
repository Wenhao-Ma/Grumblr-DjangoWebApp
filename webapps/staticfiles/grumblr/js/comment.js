
function getComments(id) {
    var all_comments = $("#comments-"+id);
    $.get("/grumblr/get-comment/"+id).done(function (data) {
        all_comments.html('');
        for (var i = 0; i < data.comments.length; i++) {
            var comment = data.comments[i];
            all_comments.append(commentHTML(comment));
        }
    });
}

function showComments() {
    var id = $(this).attr('id').substring(6);
    var comment_place = $("#show-comment"+id);
    if (comment_place.css("display") == "none") {
        comment_place.show();
        getComments(id);
    } else {
        comment_place.hide();
        $("#comments-"+id).html("");
    }
}

function inputNotEmpty() {
    var id = $(this).attr('id').substring(13);
    var btn = $('#comment-form-'+id+ ' button');
    $('#comment-form-'+id+ ' input[name=comment]').on('keyup', function () {
         if ($(this).val()) {
             btn.attr('disabled', false);
         } else {
             btn.attr('disabled', true);
         }
    });
}

function submit(event) {
    event.preventDefault(); // Prevent form from being submitted
    var id = $(this).attr('id').substring(13);

    $.post('/grumblr/add-comment/'+id, $('#comment-form-'+id).serializeArray()).done(function (data) {
        getComments(id);
        $('#comment-form-'+id+ ' input[name=comment]').val("");
        $('#comment-form-'+id+ ' button').attr('disabled', true);
    });
}

function commentHTML(comment) {
    var html =
        "<div style='font-size: 0.8em'>" +
            "<div class='row'>" +
                "<div class='col-sm-1'>" +
                    "<a href='/grumblr/home/"+comment.username+"'>" +
                        "<img class='comment-photo' src='/grumblr/photo/" + comment.username + "'>" +
                    "</a>" +
                "</div>" +
                "<div class='col-sm-11'>" +
                    "<p style='margin: 0'>" +
                        "<a class='text-body' href='/grumblr/home/" + comment.username + "'>" +
                            "<b>" + comment.username + "</b>" +
                        "</a>" +
                        ": " + comment.content +
                    "</p>" +
                    "<i class='time' style='color: #6c757d'>" + comment.time + "</i><br>" +
                "</div>" +
            "</div>" +
        "</div>" +
        "<hr>";
    return html;
}

$(function () {
    console.log("OK2");
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


    $(".comment-button").click(showComments);

    $('.comment-form').each(inputNotEmpty);

    $('.comment-form').on('submit', submit);

});