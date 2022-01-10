//Show or hide a reply
function showReply(btn, id){
    elmnt = document.getElementById(id);
    elmnt.style.display = "block";
    setTimeout(function(){
        if (btn.value.length < 1){
            elmnt.style.display="none";
        }
    }, 120000)
}

//TOF
const content = document.getElementById("blog-post-content");
if(content){
    const heads = content.querySelectorAll("h1");

    if (heads.length != 0){
        
        const accordion = document.getElementById("tof-links");
        let i = 0;
	heads.forEach((head) =>{
		//console.log(head.textContent.length);
            if (head.textContent.length > 5){
                let new_link = document.createElement("span");
        new_link.classList.add("tof-link");
        new_link.textContent = (i+1).toString()+" - "+head.textContent;
        new_link.addEventListener("click", () =>{
            head.scrollIntoView();
        })
        accordion.append(new_link);
	i++;
            }
        
    }) 
    }
    else{
        document.getElementById("toof").style.display = "none";
    }
    
}


// Open login and signup modal
const login = document.getElementById("login-btn2");
if(login ){
    login.addEventListener("click", () =>{
        const loginbtn = document.getElementById("login-btn");
        document.getElementById("close-signup-modal").click();
        loginbtn.click();
    })
}

const register = document.getElementById("register-btn");
if(register){
    register.addEventListener("click", () =>{
        const signup = document.getElementById("signup-btn");
        document.getElementById("close-login-modal").click();
        signup.click();
    })
}


/*SCROL TO TOP */

$(document).ready(function() {
    $(window).scroll(function() {
    if ($(this).scrollTop() > 20) {
    $('#toTopBtn').fadeIn();
    } else {
    $('#toTopBtn').fadeOut();
    }
    });
    
    $('#toTopBtn').click(function() {
    $("html, body").animate({
    scrollTop: 0
    }, 1000);
    return false;
    });
    });
