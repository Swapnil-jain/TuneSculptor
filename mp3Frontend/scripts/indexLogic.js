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

  const dropArea = document.querySelector(".drop_box"),
    button = dropArea.querySelector("button"),
    input = dropArea.querySelector("input");

  button.onclick = () => {
    input.click();
  };

  input.addEventListener("change", function (e) {

    //This section dynamically replaces the part of html under drop_box with the following html.
    let fileName = e.target.files[0].name;
    let filedata = `
    <header>
        <h4>${fileName}</h4>
    </header>
    <form id="upload-form">
      <button type="submit" class="up-btn">Upload</button>
    </form>
  `;
    dropArea.innerHTML = filedata;

    // Attach the event listener after the form is added to the DOM
    const uploadForm = document.getElementById("upload-form");
    if (uploadForm) {
      uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const file = input.files[0]; // Use the file already selected
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
});
