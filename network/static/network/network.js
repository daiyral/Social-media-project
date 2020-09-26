document.addEventListener('DOMContentLoaded',function(){
   var username=window.location.pathname;
   username=username.substring(username.lastIndexOf('/')+1);//get username we are looking at

   var path=window.location.pathname;
   var page=path.substring(1,path.lastIndexOf('/'));//get the page we are on
   if(page=="profile")//if we are on profile page go to view_profile
    if(document.querySelector('#follow_btn')!=null)
        view_profile(username)
   if(document.querySelector('#follow_btn')!=null)
   {
       document.querySelector('#follow_btn').onclick=()=>{
           return follow(username)
       }
   }
   if(document.querySelector('.card')!=null)
   {
       view_cards()
       window.onclick = e =>{
            if(e.target.title=='like')
                update_likes(e.target.id)
            if(e.target.title=='edit')
                edit_post(e.target.id)    
       }
   }
   //set sidebar height according to page
   document.querySelector('.sidebar').style.height=document.documentElement.scrollHeight+'px';

});
function view_cards(){
   fetch('/like/1',{
       method:'GET'
   })
   .then(response=>response.json())
   .then(liked_posts=>{
       console.log(liked_posts)
       if(liked_posts!=0)
       {
           liked_posts.forEach(liked_post=>
            {
                if(document.getElementById(`${liked_post.id}`)!=null)
                     document.getElementById(`${liked_post.id}`).style.color='red';
                if(document.getElementById(`${liked_post.id}_cnt`)!=null)     
                document.getElementById(`${liked_post.id}_cnt`).style.color='red';
            })
            
       }
   })
}

//this func sets the follow and unfollow button according to if the user is followed or not
function view_profile(username){
    const follow_btn= document.querySelector('#follow_btn');
    fetch(`/follow/${username}/""`,{
        method:'GET'
    })
    .then(response=>response.json())
    .then(is_followed=>{
        console.log(is_followed)
        if(is_followed==1)//1 means user is followed
            follow_btn.innerHTML="Unfollow";  
        else//0 means user is not followed
            follow_btn.innerHTML="Follow";      
        
    })
  


}
function edit_post(id){
    
    id_num=id.substring(id.lastIndexOf('_')+1);
    edit_btn=document.getElementById(`edit_btn_${id_num}`)
    post_text=document.getElementById(`body_${id_num}`);
    text_area=document.getElementById(`edit_body_${id_num}`);
    submit=document.getElementById(`edit_submit_${id_num}`);
    cancel=document.getElementById(`edit_cancel_${id_num}`);
    old_text=post_text.innerHTML;
    post_text.innerHTML='';
    text_area.style.display='block';
    text_area.value=old_text;
    submit.style.display='inline-block';
    cancel.style.display='inline-block';
    cancel.onclick=()=>{
        text_area.style.display='none';
        submit.style.display='none';
        cancel.style.display='none';
        post_text.innerHTML=old_text;
        return 
    }
    submit.onclick=()=>{
        post_text.innerHTML=text_area.value;
        try{
            if(text_area.value=="")throw "Post cannot be empty";
            if(text_area.value.length<2) throw "Post must have at least 2 characters";
            if(text_area.value.length>500)throw "Post cannot be over 500 characters";
        }
        catch(err){
            document.querySelector('#error').innerHTML=err;
            return edit_post(id)
        }
        
    text_area.style.display='none';
    submit.style.display='none';
    cancel.style.display='none';   
      fetch(`/edit_post/${id_num}`,{
            method:'POST',
            body:JSON.stringify({
                text:`${text_area.value}`
            })
        })
        .then(response=>response.json())
        .then(result=>{
            console.log(result)
        })
    }
    
 
}
function update_likes(id)
{
    var like_cnt=document.getElementById(`${id}_cnt`);
    var like_icon=document.getElementById(`${id}`);
        fetch(`/like/${id}`,{
            method:'POST'
        })
        .then(response=>response.json())
        .then(likes=>{
            console.log(likes);
            if(like_cnt.innerHTML<likes)
            {
                like_cnt.style.color='red';
                like_icon.style.color='red';
            }
            else
            {
                like_cnt.style.color='rgb(175,175,175)';
                like_icon.style.color='rgb(175,175,175)';
               
            }
            like_cnt.innerHTML=likes;
        })
   
}    


function follow(username){ 
    var mission="";
    var btn_text="";
    const follow_btn= document.querySelector('#follow_btn');
    if (follow_btn.innerHTML =="Follow")
    {
        mission="follow";
        btn_text="Unfollow";
    }
        
    else
    {
        mission="unfollow"
        btn_text="Follow";
    }
    
    fetch(`/follow/${username}/${mission}`,{
        method:'POST'
    })
    .then(response=>response.json())
    .then(followers=>{
        follow_btn.innerHTML=btn_text;
        document.querySelector('#followers_cnt').innerHTML=followers;
    })
}