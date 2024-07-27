document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const response = await fetch("http://mp3converter.com/login", {
    method: "POST",
    headers: {
      Authorization: "Basic " + btoa(username + ":" + password),
    },
    credentials: "include", //Includes the cookies in the request.
  });

  if (response.ok) {  
    alert("Login successful");
  } else {
    const errorData = await response.json();
    console.log("Error message:", errorData.error);
    alert("Login failed");
  }
});

document.getElementById("upload-form").addEventListener("submit", async (e) => {
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
    alert("File uploaded successfully");
  } else {
    const errorData = await response.json();
    console.log("Error message:", errorData.error);
    alert("File upload failed");
  }
});
