$(document).ready(function() {
  $.ajax({
    type: "GET",
    url: "/get_like_status/",
    success: function(response) {
      $(".like-button").each(function() {
        var postId = $(this).data("post-id");
        var heartIcon = $("#heart-icon-" + postId);
        if (response[postId]) {
          heartIcon.addClass("fas");
        }
      });
    },
    error: function(xhr, status, error) {
      console.log(error);
    }
  });
});


function likeButtonClicked(buttonElement) {
  var postId = $(buttonElement).data("post-id");
  var heartIcon = $("#heart-icon-" + postId);
  var likeCount = $("#like-count-" + postId);

  $.ajax({
    type: "POST",
    url: "/like_post/" + postId + "/",
    data: {
      post_id: postId,
      csrfmiddlewaretoken: csrfToken,
    },

    success: function(response) {
        if (response.is_liked) {
          heartIcon.addClass("fas");
          likeCount.text(response.like_count);

        } else {
          heartIcon.removeClass("fas");
          likeCount.text(response.like_count);
        }
      },
      error: function(xhr, status, error) {
        console.log(error);
      }
  });
}