<template>
<div>
  <nav class="bg-dark">
    <router-link to='/home'
                 style="font-size: 45px"
                 class="text-style"
                 :class="{disabled: $route.meta.hideNavbar}">MovieBuddy</router-link>
  </nav>
  <nav class="navbar navbar-expand-lg navbar-light" style="background-color: white">
  <div v-if="!$route.meta.hideNavbar" class="collapse navbar-collapse" id="navbarNav"  style="margin-bottom: -70px">
    <ul class="navbar-nav">
      &nbsp;&nbsp;&nbsp;
      <li class="nav-item active">
        <router-link to="/home" class="text-style btn home" tag="button"></router-link>
      </li> &nbsp;&nbsp;&nbsp;
      <li class="nav-item active">
        <router-link to="/profile" class="text-style btn profile" tag="button"></router-link>
      </li>&nbsp;&nbsp;&nbsp;&nbsp;
      <li class="nav-item active" v-if="user.admin">
        <router-link to="/admin" class="text-style btn admin" tag="button"></router-link>
      </li>
      <li>
        <button class="text-style btn logout" @click="logoutUser"></button>
      </li>
    </ul>
  </div>
</nav>
  </div>
</template>

<script>
export default {
  data(){
    return {
      user: JSON.parse(localStorage['user']),
      n:0
    }
  },
  methods:{
    logoutUser(){
      fetch("http://localhost:5000/api/logout", {
        method:"GET",
        headers:{
          "Content-Type":"application/json",
          "Authentication-Token":this.$store.state.token
        }
      })
          .then(response => {
            if (response.ok){
              localStorage['user'] = null;
              localStorage['token'] = null;
              this.$router.push({
                name:"login"
              });
                  console.log("Logged Out");
                  window.scrollTo(0,0)
                }
            else
                {
                  console.log("Error")
                }
            response.json()
          })
          .then(data => console.log(data))
          .catch(err => console.log(err))
    }
  },
    created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
    }
}
</script>

<style scoped>

  .text-style{
    text-align: left !important;
    font-size:30px;
    text-decoration: none !important;
    font-family: fantasy !important;
    color: floralwhite !important;
  }

  .disabled {
    pointer-events: none;
  }

  .home{
    width: 75px;
    height: 70px;
    background-image: url(https://cdn-icons-png.flaticon.com/128/1946/1946436.png);
    background-size: 80%;
    background-repeat: no-repeat;
    background-clip: padding-box;
  }

  .profile{
    width: 75px;
    height: 70px;
    background-image: url(https://cdn-icons-png.flaticon.com/128/3033/3033143.png);
    background-size: 80%;
    background-repeat: no-repeat;
    background-clip: border-box;
  }

  .admin{
    width: 75px;
    height: 70px;
    background-image: url(https://cdn-icons-png.flaticon.com/128/7542/7542245.png);
    background-size: 80%;
    background-repeat: no-repeat;
    background-clip: border-box;
  }

  .logout{
      width: 75px;
      height: 70px;
      background-image: url(https://cdn-icons-png.flaticon.com/128/1828/1828479.png);
      background-size: 80%;
      background-repeat: no-repeat;
      background-clip: border-box;
      margin-left: 1000px;
    margin-bottom: 2px;
  }
</style>