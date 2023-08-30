$(document).ready(function() {
  var heartIcon = $("#heart-icon");

  $.ajax({
    type: "GET",
    url: "/get_like_status/" + postId + "/",
    success: function(response) {
      if (response.is_liked) {
        heartIcon.addClass("fas");
      }
    },
    error: function(xhr, status, error) {
      console.log(error);
    }
  });

});

function likeButtonClicked(buttonElement) {
  var heartIcon = $("#heart-icon");
  var likeCount = $(".like-count");
  var postId = $(buttonElement).data("post-id");

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