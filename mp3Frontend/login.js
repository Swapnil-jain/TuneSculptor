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
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;

      const response = await fetch("http://mp3converter.com/login", {
        method: "POST",
        headers: {
          Authorization: "Basic " + btoa(username + ":" + password),
        },
        credentials: "include", // Includes the cookies in the request.
      });

      if (response.ok) {
        alert("Login successful");
        window.location.href = "/";
      } else {
        const errorData = await response.json();
        console.log("Error message:", errorData.error);
        alert("Login failed");
      }
    });
  }
});
