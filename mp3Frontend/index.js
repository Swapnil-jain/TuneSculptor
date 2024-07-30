document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await fetch("http://mp3converter.com/validate_token", {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      window.location.href = "http://mp3converter.com/login.html";
    }
  } catch (error) {
    console.error("Error validating token:", error);
    window.location.href = "http://mp3converter.com/login.html";
  }

  const uploadForm = document.getElementById("upload-form");
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const file = document.getElementById("file").files[0];
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://mp3converter.com/upload", {
        method: "POST",
        body: formData,
        credentials: "include", // Include cookies in requests
      });

      if (response.ok) {
        window.location.href = "http://mp3converter.com/thankyou.html";
      } else {
        const errorData = await response.json();
        console.log("Error message:", errorData.error);
        alert("File upload failed");
      }
    });
  }
});
