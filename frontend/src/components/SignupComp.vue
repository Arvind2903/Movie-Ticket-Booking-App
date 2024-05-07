<template>
<div>
  <br>
  <h2>Sign up to use MovieBuddy</h2>
  <p><strong>(* marked fields are important)</strong></p>
  <div class="container card-group mt-4">
    <form @submit.prevent="signUp">
      <p style="text-align: left">*Username:</p>
      <input
        type="text"
        class="form-control"
        placeholder="Please choose a username"
        v-model="username">
      <br/>
      <p style="text-align: left">*Email Address: <b>(cannot be changed later)</b> </p>
      <input
        type="text"
        class="form-control"
        size="28"
        placeholder="Please enter your email address"
        v-model="email">
      <br/>
      <p style="text-align: left">*Full Name:</p>
      <input
        type="text"
        class="form-control"
        placeholder="Please enter your full name"
        v-model="name">
      <br/>
      <p style="text-align: left">*Phone Number:</p>
      <input
        type="number"
        class="form-control"
        placeholder="Please enter your phone number"
        v-model="phone">
      <br/>
      <p style="text-align: left">*Are you a theatre admin?</p>
      <input type="checkbox"
             id="checkbox"
             v-model="admin" />
      <label for="checkbox">{{ admin ? 'Yes' : 'No' }}</label>
      <br/>
      <p style="text-align: left">*Password:</p>
      <input
        type="password"
        class="form-control"
        placeholder="Please enter your password"
        v-model="password">
      <br/>
      <p style="text-align: left">*Confirm Password:</p>
      <input
        type="password"
        class="form-control"
        placeholder="Please confirm your password"
        v-model="confirm_password">
      <br/>
      <button
        type="submit"
        class="btn"
        style="background-image: url(https://cdn-icons-png.flaticon.com/512/9633/9633868.png);
               background-size: 100%; width: 75px; height: 75px">
      </button>
      <p>Sign Up</p>
      <div v-if="error" class="alert alert-warning alert-dismissible fade show mt-5" role="alert">
    <strong>{{error}}</strong>
  </div>
  <div v-if="password_error" class="alert alert-warning alert-dismissible fade show mt-5" role="alert">
    <strong>{{password_error}}</strong>
  </div>
    </form>
  </div>
</div>
</template>

<script>
export default {
  data(){
    return{
      username:null,
      email:null,
      name:null,
      phone:null,
      admin:false,
      password:null,
      confirm_password:null,
      error:null,
      password_error:null
    }
  },
  methods:{
    signUp(){
      if(!this.username || !this.email || !this.name || !this.password || !this.phone){
        this.error = "Please add all required fields"
      }
      else if (this.password !== this.confirm_password){
          this.error = null;
          this.password_error = "Passwords don't match!!!"
      }
      else
        {
          fetch('http://localhost:5000/api/signup',{
          method:'POST',
          headers:{
          "Content-Type":"application/json"
        },
          body:JSON.stringify({username:this.username, email:this.email, name:this.name,
          phone:this.phone, admin:this.admin, password:this.password})
        })
              .then((response) => {
                if (response.ok){
                  this.$router.push({
                    name:"login"
                  })
                  console.log("Signed Up");
                  window.scrollTo(0,0);
                }
                else if(response.status===405){
                  this.error = response.statusText;
                }
                else{
                  this.error = response.statusText;
                }
              })
              .catch(error => console.log(error))
        }
      }
    }
}
</script>

<style scoped>
.card-group{
  margin: 41%;
}
input::placeholder{
  text-align: center;
}
</style>