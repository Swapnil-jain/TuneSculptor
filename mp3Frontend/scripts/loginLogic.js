document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await fetch("http://mp3converter.com/validate_token", {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      window.location.href = "/";
    }
  } catch (error) {
    console.error("Error validating token:", error);
  }

  const loginForm = document.getElementById("login-form");
  const loginMessageDiv = document.getElementById("login-message"); // Get the error message div
  const registerForm = document.getElementById("register-form");
  const registerMessageDiv = document.getElementById("register-message");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      // Show the loading icon
      const loginButton = document.getElementById("login-button");
      const loadingIcon = document.getElementById("loading-icon-1");
      loginButton.disabled = true; // Disable the button to prevent multiple submissions
      loadingIcon.classList.add("loading"); // Show the loading icon

      //selecting the usernames and passwords.
      const username = document.getElementById("email").value;
      const password = document.getElementById("password").value;
      
      try {
        const response = await fetch("http://mp3converter.com/login", {
          method: "POST",
          headers: {
            Authorization: "Basic " + btoa(username + ":" + password),
          },
          credentials: "include", // Includes the cookies in the request.
        });

        if (response.ok) {
          loginMessageDiv.textContent = "Login Successful";
          loginMessageDiv.style.color = "green";
          loginMessageDiv.style.display = "block";

          setTimeout(() => {  //the 1 second timeout is to enhance user experience so he can actually read the login successful msg.
            window.location.href = "/";
          }, 1000);
        } else {
          const errorData = await response.json();
          loginMessageDiv.textContent = "Incorrect username/password";
          loginMessageDiv.style.color = "red";
          loginMessageDiv.style.display = "block";
        }
      } catch (error) {
        console.error("Error logging in:", error);
        loginMessageDiv.textContent = "An error occurred. Please try again.";
        loginMessageDiv.style.color = "red";
        loginMessageDiv.style.display = "block";
      } finally {
        // Hide the loading icon and re-enable the button after the process is complete
        loadingIcon.classList.remove("loading");
        loginButton.disabled = false;
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      // Show the loading icon
      const registerButton = document.getElementById("register-button");
      const loadingIcon = document.getElementById("loading-icon-2");
      registerButton.disabled = true; // Disable the button to prevent multiple submissions
      loadingIcon.classList.add("loading"); // Show the loading icon
      
      // selecting the usernames and passwords
      const username = document.getElementById("signup-email").value;
      const password = document.getElementById("signup-password").value;
      const passwordConfirmation =
        document.getElementById("passwordConfirm").value;

      //ensure both passwords are same.
      if (password != passwordConfirmation) {
        registerMessageDiv.textContent = "Passwords do not match";
        registerMessageDiv.style.color = "red";
        registerMessageDiv.style.display = "block";
        loadingIcon.classList.remove("loading"); //remove the loading icon.
        registerButton.disabled = false; //reable the register button.
        return;
      }

      try {
        const response = await fetch("http://mp3converter.com/register", {
          method: "POST",
          headers: {
            Authorization: "Basic " + btoa(username + ":" + password),
          },
        });

        if (response.status === 201) {
          registerMessageDiv.textContent = "Registration Successful";
          registerMessageDiv.style.color = "green";
          registerMessageDiv.style.display = "block";

          setTimeout(() => {
            window.location.href = "http://mp3converter.com/login.html";
          }, 1000);
        } else if (response.status === 409) {
          registerMessageDiv.textContent = "You already have an account.";
          registerMessageDiv.style.color = "red";
          registerMessageDiv.style.display = "block";
        }
      } catch (error) {
        console.error("Error registering:", error);
        registerMessageDiv.textContent = "An error occurred. Please try again.";
        registerMessageDiv.style.color = "red";
        registerMessageDiv.style.display = "block";
      } finally {
        // Hide the loading icon and re-enable the button after the process is complete
        loadingIcon.classList.remove("loading");
        registerButton.disabled = false;
      }
    });
  }
});