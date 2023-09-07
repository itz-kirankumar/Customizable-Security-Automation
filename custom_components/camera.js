document.addEventListener("DOMContentLoaded", () => {
  const video = document.createElement("video");
  video.setAttribute("playsinline", "");
  document.getElementById("camera-container").appendChild(video);

  navigator.mediaDevices
    .getUserMedia({ video: true, audio: false })
    .then((stream) => {
      video.srcObject = stream;
    })
    .catch((error) => {
      console.error("Error accessing the camera:", error);
    });
});
