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
        console.log("isFollowing value is: ", isFollowing);

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

$(document).ready(function() {
  $.ajax({
    type: "GET",
    url: "/get_star_status/",
    success: function(response) {
      $(".rating-star").each(function() {
        var star = $(this);
        var rating = star.data("rating");
        var evidenceId = star.data("evidence-id");
        if (response[evidenceId] && rating <= response[evidenceId]) {
          star.addClass("selected");
        }
      });
    },
    error: function(xhr, status, error) {
      console.log(error);
    }
  });
});


$(document).ready(function() {
  var avg_star = parseFloat($("p[data-avg]").data("avg"));
  var full_stars = Math.floor(avg_star);
  var partial_star = avg_star - full_stars;

  if (avg_star === 0) {
    return;
  }

  $(".rating-avg-star").each(function() {
    var star = $(this);
    var rating = star.data("rating-avg");
    if (rating <= full_stars) {
      star.addClass("selected");
      console.log(star.width());
    } else if (rating === full_stars + 1) {
      star.addClass("selected");
      var starWidth = star.width();
      console.log("star width:",  starWidth);
      var partialWidth = starWidth * partial_star;
      star.css('width', partialWidth + 'px');
    }
  });
});

$(document).ready(function() {
  function checkNewNotifications() {
    $.ajax({
      url: '/api/notifications/check',
      method: 'GET',
      success: function(response) {
        if (response.hasNewNotification) {
          showNewNotification();
        }
      },
      error: function(error) {
        console.log('通知の問い合わせに失敗しました。', error);
      }
    });
  }

  checkNewNotifications();

  $('#notification-link').click(function() {
    $('#notification-icon').empty();
  });

  function showNewNotification() {
    $('#notification-icon').html('🔴');
  }
});