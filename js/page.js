setInterval(() => {
  let body = document.querySelector('body');
  let html = document.querySelector('html');
  let height = Math.max( body.scrollHeight, body.offsetHeight,
                         html.clientHeight, html.scrollHeight, html.offsetHeight );
  body.style.height=(height)+"px";
  html.style.height = (height)+ 'px';
}, 100);
