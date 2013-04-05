function setZoom(img, dir, width, height, margin, zIndex, delay) {
  setTimeout(function() {
    if (img.dir==dir) {
      img.style.width=width;
      img.style.height=height;
      img.style.margin=margin;
      img.style.zIndex=zIndex;
      img.parentNode.parentNode.style.zIndex=zIndex;
    }
  }, delay);
}

function larger(img, width, height) {
  img.dir='rtl';
  now=parseInt(img.style.zIndex);
  for (i=now+1; i<=10; i++) {
    w=(width*(10+i))/20+'px';
    h=(height*(10+i))/20+'px';
    m=(-i)+'px 0 0 '+(-width*i/40)+'px';
    setZoom(img, 'rtl', w, h, m, i, 20*(i-now));
  }
}

function smaller(img, width, height) {
  img.dir='ltr';
  now=parseInt(img.style.zIndex);
  for (i=now-1; i>=0; i--) {
    w=(width*(10+i))/20+'px';
    h=(height*(10+i))/20+'px';
    m=(-i)+'px 0 0 '+(-width*i/40)+'px';
    setZoom(img, 'ltr', w, h, m, i, 20*(now-i));
  }
}
