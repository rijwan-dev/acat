// Animate the page intro features (pop in one by one)
window.addEventListener('DOMContentLoaded', () => {
  const features = document.querySelectorAll('.feature');
  features.forEach((el, i) => {
    el.style.opacity = '0';
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'scale(1.03)';
      setTimeout(()=>{el.style.transform='scale(1)';},500);
    }, 350 + i * 240);
  });

  // Animate subtitle pulsate and brand
  const subtitle = document.querySelector('.subtitle-anim');
  if(subtitle) {
    setInterval(() => {
      subtitle.style.opacity = subtitle.style.opacity === "0.56" ? "1" : "0.56";
    }, 1850);
  }
});
