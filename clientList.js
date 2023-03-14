'use strict';
const e = React.createElement;

function clientList(props) {
    const [liked,setLiked] = React.useState(false)

    if (liked) {
      return 'You liked this.';
    }

    // return (
    //   <button onclick={()=>setLiked(true)}>Like</button>
    // )
    return e(
      'button',
      { onClick: () => setLiked(true) },
      'Like'
    );
}

const domContainer = document.querySelector('#clientList');
const root = ReactDOM.createRoot(domContainer);
root.render(e(clientList));