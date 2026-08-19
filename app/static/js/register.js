document.addEventListener("DOMContentLoaded", function () {
  /* =====================================================
       ELEMENTS
    ===================================================== */
  const form = document.getElementById("registerForm");

  const step1 = document.getElementById("step1");
  const step2 = document.getElementById("step2");

  const nextBtn = document.getElementById("nextBtn");
  const backBtn = document.getElementById("backBtn");

  const indicator1 = document.getElementById("stepIndicator1");

  const indicator2 = document.getElementById("stepIndicator2");

  const stepLine = document.getElementById("stepLine");

  const username = document.getElementById("username");

  const email = document.getElementById("email");

  const fullName = document.getElementById("full_name");

  const password = document.getElementById("password");

  const confirmPassword = document.getElementById("confirm_password");

  const strengthBar = document.getElementById("strengthBar");

  const strengthText = document.getElementById("strengthText");

  const matchMessage = document.getElementById("matchMessage");

  /* =====================================================
       STEP 1 VALIDATION
    ===================================================== */

  function validateStep1() {
    const usernameValue = username.value.trim();

    const emailValue = email.value.trim();

    const fullNameValue = fullName.value.trim();

    if (!usernameValue) {
      username.focus();

      username.classList.add("is-invalid");

      return false;
    }

    if (!emailValue) {
      email.focus();

      email.classList.add("is-invalid");

      return false;
    }

    if (!email.checkValidity()) {
      email.focus();

      email.classList.add("is-invalid");

      return false;
    }

    if (!fullNameValue) {
      fullName.focus();

      fullName.classList.add("is-invalid");

      return false;
    }

    username.classList.remove("is-invalid");
    email.classList.remove("is-invalid");
    fullName.classList.remove("is-invalid");

    return true;
  }

  /* =====================================================
       NEXT
    ===================================================== */

  nextBtn.addEventListener("click", function () {
    if (!validateStep1()) {
      return;
    }

    step1.classList.remove("active-step");

    step2.classList.add("active-step");

    indicator1.classList.add("active");

    indicator2.classList.add("active");

    stepLine.classList.add("completed");

    setTimeout(function () {
      password.focus();
    }, 300);
  });

  /* =====================================================
       BACK
    ===================================================== */

  backBtn.addEventListener("click", function () {
    step2.classList.remove("active-step");

    step1.classList.add("active-step");

    indicator2.classList.remove("active");

    stepLine.classList.remove("completed");

    setTimeout(function () {
      username.focus();
    }, 300);
  });

  /* =====================================================
       PASSWORD SHOW / HIDE
    ===================================================== */

  const toggleButtons = document.querySelectorAll(".password-toggle");

  toggleButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const targetId = button.dataset.target;

      const input = document.getElementById(targetId);

      const icon = button.querySelector("i");

      if (input.type === "password") {
        input.type = "text";

        icon.classList.remove("bi-eye");

        icon.classList.add("bi-eye-slash");

        button.setAttribute("aria-label", "Hide password");
      } else {
        input.type = "password";

        icon.classList.remove("bi-eye-slash");

        icon.classList.add("bi-eye");

        button.setAttribute("aria-label", "Show password");
      }
    });
  });

  /* =====================================================
       PASSWORD REQUIREMENTS
    ===================================================== */

  const requirements = {
    length: document.getElementById("lengthRequirement"),

    uppercase: document.getElementById("uppercaseRequirement"),

    lowercase: document.getElementById("lowercaseRequirement"),

    number: document.getElementById("numberRequirement"),

    special: document.getElementById("specialRequirement"),
  };

  function updateRequirement(element, valid) {
    if (valid) {
      element.classList.add("valid");

      element.classList.remove("invalid");
    } else {
      element.classList.remove("valid");

      element.classList.add("invalid");
    }
  }

  /* =====================================================
       PASSWORD STRENGTH
    ===================================================== */

  function checkPasswordStrength() {
    const value = password.value;

    const checks = {
      length: value.length >= 8,

      uppercase: /[A-Z]/.test(value),

      lowercase: /[a-z]/.test(value),

      number: /[0-9]/.test(value),

      special: /[!@#$%^&*(),.?":{}|<>_\-+=]/.test(value),
    };

    updateRequirement(requirements.length, checks.length);

    updateRequirement(requirements.uppercase, checks.uppercase);

    updateRequirement(requirements.lowercase, checks.lowercase);

    updateRequirement(requirements.number, checks.number);

    updateRequirement(requirements.special, checks.special);

    const score = Object.values(checks).filter(Boolean).length;

    let width = 0;
    let text = "None";

    if (value.length === 0) {
      width = 0;

      text = "None";
    } else if (score <= 2) {
      width = 25;

      text = "Weak";
    } else if (score === 3) {
      width = 50;

      text = "Fair";
    } else if (score === 4) {
      width = 75;

      text = "Good";
    } else {
      width = 100;

      text = "Strong";
    }

    strengthBar.style.width = width + "%";

    strengthText.textContent = text;

    if (score <= 2) {
      strengthBar.style.background = "#dc3545";

      strengthText.style.color = "#dc3545";
    } else if (score === 3) {
      strengthBar.style.background = "#ffc107";

      strengthText.style.color = "#b58100";
    } else if (score === 4) {
      strengthBar.style.background = "#0dcaf0";

      strengthText.style.color = "#087990";
    } else {
      strengthBar.style.background = "#198754";

      strengthText.style.color = "#198754";
    }

    checkPasswordMatch();
  }

  password.addEventListener("input", checkPasswordStrength);

  /* =====================================================
       CONFIRM PASSWORD
    ===================================================== */

  function checkPasswordMatch() {
    const pass = password.value;

    const confirm = confirmPassword.value;

    if (!confirm) {
      matchMessage.textContent = "";

      matchMessage.className = "match-message";

      return false;
    }

    if (pass === confirm) {
      matchMessage.textContent = "✓ Passwords match";

      matchMessage.className = "match-message success";

      return true;
    } else {
      matchMessage.textContent = "✕ Passwords do not match";

      matchMessage.className = "match-message error";

      return false;
    }
  }

  confirmPassword.addEventListener("input", checkPasswordMatch);

  /* =====================================================
       FORM SUBMIT
    ===================================================== */

  form.addEventListener("submit", function (event) {
    const pass = password.value;

    const confirm = confirmPassword.value;

    const strongPassword =
      pass.length >= 8 &&
      /[A-Z]/.test(pass) &&
      /[a-z]/.test(pass) &&
      /[0-9]/.test(pass) &&
      /[!@#$%^&*(),.?":{}|<>_\-+=]/.test(pass);

    if (!strongPassword) {
      event.preventDefault();

      password.focus();

      return;
    }

    if (pass !== confirm) {
      event.preventDefault();

      confirmPassword.focus();

      return;
    }

    /* Loading state */

    const createBtn = document.getElementById("createBtn");

    const createText = document.getElementById("createText");

    const createLoading = document.getElementById("createLoading");

    createBtn.disabled = true;

    createText.classList.add("d-none");

    createLoading.classList.remove("d-none");
  });

  /* =====================================================
       REMOVE INVALID STATE WHEN USER TYPES
    ===================================================== */

  [username, email, fullName].forEach(function (input) {
    input.addEventListener("input", function () {
      input.classList.remove("is-invalid");
    });
  });
});
