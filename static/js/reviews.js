class ReviewsManager {
  constructor() {
    this.userId = new URLSearchParams(window.location.search).get("user_id");
    this.currentSort = "newest";
    this.selectedRating = 0;
    this.init();
  }

  init() {
    this.loadReviews();
    this.setupEventListeners();
    this.highlightActivePage();
  }

  setupEventListeners() {
    // Звезды рейтинга
    document.querySelectorAll(".star-label").forEach((star) => {
      star.addEventListener("click", (e) => {
        this.handleStarClick(e.target);
      });

      star.addEventListener("mouseenter", (e) => {
        this.handleStarHover(e.target, true);
      });

      star.addEventListener("mouseleave", (e) => {
        this.handleStarHover(e.target, false);
      });
    });

    // Кнопка отправки отзыва
    document.getElementById("submitReview")?.addEventListener("click", () => {
      this.submitReview();
    });

    // Кнопка удаления отзыва
    document.getElementById("deleteReview")?.addEventListener("click", () => {
      this.deleteReview();
    });

    // Счетчик символов
    document.getElementById("reviewComment")?.addEventListener("input", (e) => {
      this.updateCharCount(e.target);
    });

    // Фильтры
    document.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        this.handleFilterClick(e.target);
      });
    });
  }

  async loadReviews() {
    try {
      const response = await fetch(
        `/api/reviews?sort=${this.currentSort}&user_id=${this.userId}`
      );
      const data = await response.json();

      if (data.success) {
        this.updateStats(data);
        this.updateUserReview(data.user_review);
        this.renderReviews(data.reviews);
      } else {
        this.showError("Ошибка загрузки отзывов");
      }
    } catch (error) {
      console.error("Error loading reviews:", error);
      this.showError("Ошибка загрузки отзывов");
    }
  }

  updateStats(data) {
    // Обновляем статистику
    document.querySelector(".rating-number").textContent = data.average_rating;
    document.querySelector(".count-number").textContent = data.reviews_count;

    // Обновляем звезды среднего рейтинга
    const starsElement = document.querySelector(".rating-stars .stars");
    starsElement.innerHTML = this.generateStars(data.average_rating, false);
  }

  updateUserReview(userReview) {
    const reviewForm = document.getElementById("reviewForm");
    const userReviewSection = document.getElementById("userReview");

    if (userReview) {
      // Пользователь уже оставил отзыв
      reviewForm.style.display = "none";
      userReviewSection.style.display = "block";

      // Заполняем данные отзыва
      document.getElementById("userReviewStars").innerHTML = this.generateStars(
        userReview.rating,
        true
      );
      document.getElementById("userReviewComment").textContent =
        userReview.comment || "Пользователь не оставил комментарий";
      document.getElementById("userReviewTime").textContent =
        userReview.time_ago;
      document.getElementById("userReviewLikes").textContent = userReview.likes;
    } else {
      // Пользователь еще не оставлял отзыв
      reviewForm.style.display = "block";
      userReviewSection.style.display = "none";
    }
  }

  renderReviews(reviews) {
    const container = document.getElementById("reviewsList");

    if (reviews.length === 0) {
      container.innerHTML =
        '<div class="no-reviews">Пока нет отзывов. Будьте первым!</div>';
      return;
    }

    container.innerHTML = reviews
      .map(
        (review) => `
            <div class="review-item" data-review-id="${review.id}">
                <div class="review-header">
                    <div class="user-info">
                        <span class="username">${this.escapeHtml(
                          review.username
                        )}</span>
                        <div class="rating-stars">
                            <span class="stars active">${this.generateStars(
                              review.rating,
                              true
                            )}</span>
                        </div>
                    </div>
                    <div class="review-actions">
                        <span class="time-ago">${review.time_ago}</span>
                        ${
                          review.user_id != this.userId
                            ? `
                            <button class="btn-like ${
                              review.user_has_liked ? "liked" : ""
                            }" 
                                    onclick="reviewsManager.toggleLike(${
                                      review.id
                                    })">
                                <span class="like-icon">❤️</span>
                                <span class="like-count">${review.likes}</span>
                            </button>
                        `
                            : ""
                        }
                    </div>
                </div>
                <div class="review-comment">${
                  this.escapeHtml(review.comment) ||
                  "Пользователь не оставил комментарий"
                }</div>
            </div>
        `
      )
      .join("");
  }

  generateStars(rating, isActive) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    let stars = "";

    // Полные звезды
    for (let i = 0; i < fullStars; i++) {
      stars += isActive ? "★" : "⭐";
    }

    // Половина звезды
    if (hasHalfStar) {
      stars += "½";
    }

    // Пустые звезды
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
      stars += isActive ? "☆" : "☆";
    }

    return stars;
  }

  handleStarClick(star) {
    const input = star.previousElementSibling;
    this.selectedRating = parseInt(input.value);

    // Обновляем текст выбранного рейтинга
    document.getElementById("selectedRating").textContent = this.selectedRating;

    // Сбрасываем все звезды к серому
    document.querySelectorAll(".star-label").forEach((s) => {
      s.style.color = "#ddd";
    });

    // Подсвечиваем выбранные звезды
    let currentStar = star;
    while (currentStar) {
      currentStar.style.color = "#ffd700";
      currentStar = currentStar.nextElementSibling;
    }
  }

  handleStarHover(star, isHovering) {
    if (this.selectedRating > 0) return; // Не показывать ховер если уже выбран рейтинг

    const stars = document.querySelectorAll(".star-label");

    if (isHovering) {
      // При ховере подсвечиваем звезды
      let currentStar = star;
      while (currentStar) {
        currentStar.style.color = "#ffd700";
        currentStar = currentStar.nextElementSibling;
      }
    } else {
      // При уходе мыши возвращаем к серому
      stars.forEach((s) => {
        s.style.color = "#ddd";
      });
    }
  }

  updateCharCount(textarea) {
    const count = textarea.value.length;
    const charCount = document.getElementById("charCount");
    charCount.textContent = count;

    if (count > 450) {
      charCount.parentElement.classList.add("warning");
    } else {
      charCount.parentElement.classList.remove("warning");
    }
  }

  async submitReview() {
    if (!this.selectedRating) {
      this.showError("Пожалуйста, поставьте оценку");
      return;
    }

    const comment = document.getElementById("reviewComment").value.trim();

    try {
      const response = await fetch("/api/reviews", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          rating: this.selectedRating,
          comment: comment,
          user_id: parseInt(this.userId), // Добавляем user_id в тело запроса
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка сервера");
      }

      const data = await response.json();

      if (data.success) {
        this.showSuccess("Отзыв успешно отправлен!");
        this.resetForm();
        this.loadReviews();
      } else {
        this.showError("Ошибка при отправке отзыва");
      }
    } catch (error) {
      console.error("Error submitting review:", error);
      this.showError(error.message);
    }
  }

  async deleteReview() {
    if (!confirm("Вы уверены, что хотите удалить ваш отзыв?")) {
      return;
    }

    try {
      const response = await fetch(`/api/reviews/user`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: parseInt(this.userId), // Добавляем user_id в тело запроса
        }),
      });

      if (!response.ok) {
        throw new Error("Ошибка сервера");
      }

      const data = await response.json();

      if (data.success) {
        this.showSuccess("Отзыв удален");
        this.loadReviews();
      } else {
        this.showError("Ошибка при удалении отзыва");
      }
    } catch (error) {
      console.error("Error deleting review:", error);
      this.showError("Ошибка при удалении отзыва");
    }
  }

  async toggleLike(reviewId) {
    try {
      const reviewElement = document.querySelector(
        `[data-review-id="${reviewId}"]`
      );
      const likeButton = reviewElement.querySelector(".btn-like");
      const likeCount = reviewElement.querySelector(".like-count");

      const isLiked = likeButton.classList.contains("liked");
      const endpoint = isLiked ? "unlike" : "like";

      const response = await fetch(`/api/reviews/${reviewId}/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: parseInt(this.userId), // Добавляем user_id в тело запроса
        }),
      });

      if (!response.ok) {
        throw new Error("Ошибка сервера");
      }

      const data = await response.json();

      if (data.success) {
        // Обновляем UI
        const currentLikes = parseInt(likeCount.textContent);
        likeCount.textContent = isLiked ? currentLikes - 1 : currentLikes + 1;
        likeButton.classList.toggle("liked", !isLiked);
      }
    } catch (error) {
      console.error("Error toggling like:", error);
      this.showError("Ошибка при оценке отзыва");
    }
  }

  handleFilterClick(button) {
    // Убираем активный класс со всех кнопок
    document.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.classList.remove("active");
    });

    // Добавляем активный класс к нажатой кнопке
    button.classList.add("active");

    // Устанавливаем новую сортировку и перезагружаем
    this.currentSort = button.dataset.sort;
    this.loadReviews();
  }

  resetForm() {
    this.selectedRating = 0;
    document.getElementById("reviewComment").value = "";
    document.getElementById("selectedRating").textContent = "0";
    document.getElementById("charCount").textContent = "0";
    document.querySelectorAll(".star-label").forEach((star) => {
      star.style.color = "#ddd";
    });
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  showError(message) {
    alert(`Ошибка: ${message}`);
  }

  showSuccess(message) {
    alert(message);
  }

  highlightActivePage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-link");

    navLinks.forEach((link) => {
      const linkPath = link.getAttribute("href").split("?")[0];
      if (linkPath === currentPath) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });
  }
}

// Инициализация при загрузке страницы
let reviewsManager;
document.addEventListener("DOMContentLoaded", function () {
  reviewsManager = new ReviewsManager();
});
