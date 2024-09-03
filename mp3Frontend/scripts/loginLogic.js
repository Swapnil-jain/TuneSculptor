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
      const username = document.getElementById("email").value;
      const password = document.getElementById("password").value;

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

        // Add a 1-second delay before redirecting; to help users see the success message.
        setTimeout(() => {
          window.location.href = "/";
        }, 1000);

      } else {
        const errorData = await response.json();
        console.log("Error message:", errorData.error);
        loginMessageDiv.textContent = "Incorrect username/password";
        registerMessageDiv.style.color = "red";
        loginMessageDiv.style.display = "block";
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("signup-email").value;
      const password = document.getElementById("signup-password").value;
      const passwordConfirmation =
        document.getElementById("passwordConfirm").value;

      if (password != passwordConfirmation) {
        registerMessageDiv.textContent = "Passwords do not match";
        registerMessageDiv.style.color = "red";
        registerMessageDiv.style.display = "block";
      }
      else {
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

          // Add a 1-second delay before redirecting; to help users see the success message.
          setTimeout(() => {
            window.location.href = "http://mp3converter.com/login.html";
          }, 1000);
        } 
        else if (response.status === 409) {
          registerMessageDiv.textContent = "You already have an account.";
          registerMessageDiv.style.color = "red";
          registerMessageDiv.style.display = "block";
        }
        else {
          registerMessageDiv.textContent =
            "Something went wrong during registration";
          registerMessageDiv.style.color = "red";
          registerMessageDiv.style.display = "block";
        }
      }
    });
  }
});