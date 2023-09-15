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

function followButtonClicked() {
  $.ajax({
    type: "POST",
    url: "/follow/" + userId + "/",
    data: {
      user_id: userId,
      csrfmiddlewaretoken: csrfToken,
    },
    success: function(response) {
      if (response.success) {
        isFollowing = response.is_following;
        console.log("isFollowing value is: ", isFollowing);  // デバッグ用

        if (isFollowing === true) {
          $("#follow-button").addClass("follow-btn");
        } else {
          $("#follow-button").removeClass("follow-btn");
        }
        $("#follow-button").text(isFollowing ? "フォロー中" : "フォロー");
        $("#follow-button").attr("data-following", isFollowing);
      }
    }
  });
}

$(document).ready(function() {
  $.ajax({
    type: "GET",
    url: "/get_follow_status/" + userId + "/",
    data: {
      user_id: userId,
    },
    success: function(response) {
      if (response.success) {
        $("#follow-button").addClass("follow-btn");
        $("#follow-button").text("フォロー中");
      }
    },
    error: function(xhr, status, error) {
      console.log(error);
    }
  });
});


$('.post-image, .evidence-image, .evidence-modal-image').click(function() {
  const modal = $('#modal');
  const modalImage = $('#modal-image');

  modalImage.attr('src', $(this).attr('src'));
  modal.show();
});

$('#close-modal').click(function() {
  $('#modal').hide();
});

/* 証拠画像プレビュー */
$(document).ready(function() {
  $('.image-post').on('change', function() {

    const files = this.files;
    $.each(files, function(i, file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const img = $('<img>').attr({
          src: e.target.result,
          width: 200,
          height: 200,
          class: 'preview'
        });
        $('#preview').append(img);
      };
      reader.readAsDataURL(file);
    });
  });
});

$('.evidence-btn').click(function() {
  var postId = $(this).data('post-id');

  $('#hiddenPostId').val(postId);
});

/* スター評価 */
$(".star").click(function() {
  const rating = $(this).data("rating");
  setRating(rating);
  $('#star_rating').val(rating);
});

function setRating(rating) {
  $(".star").each(function() {
    if ($(this).data("rating") <= rating) {
      $(this).addClass("selected");
    } else {
      $(this).removeClass("selected");
    }
  });
}
