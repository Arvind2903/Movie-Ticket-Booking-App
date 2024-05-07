<template>
<div>
  <br>
  <h2>Edit Your Profile</h2>
  <p><strong>(* marked fields are important)</strong></p>
  <div class="container card-group mt-4">
    <form @submit.prevent="editProfile">
      <p style="text-align: left">*Username:</p>
      <input
        type="text"
        class="form-control"
        placeholder="Please choose a username"
        v-model="username">
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
      <button
        type="submit"
        class="btn"
        style="background-image: url(https://cdn-icons-png.flaticon.com/128/7046/7046131.png);
               background-size: 100%; width: 75px; height: 75px">
      </button>
      <div v-if="error" class="alert alert-warning alert-dismissible fade show mt-5" role="alert">
        <strong>{{error}}</strong>
      </div>
    </form>
  </div>
</div>
</template>

<script>
import {mapMutations} from "vuex";

export default {
  data(){
    return{
      user:this.$store.state.user,
      username:null,
      name:null,
      phone:null,
      error:null,
    }
  },
  methods:{
    ...mapMutations(["setUser"]),
    editProfile(){
      if(!this.username || !this.name || !this.phone){
        this.error = "Please add all required fields"
      }
      else
        {
          fetch('http://localhost:5000/api/user',{
          method:'PUT',
          headers:{
          "Content-Type":"application/json",
            "Authentication-Token": this.$store.state.token
        },
          body:JSON.stringify({username:this.username, name:this.name, phone:this.phone})
        })
            .then(resp => resp.json())
            .then(data => {
              this.$store.state.user = data;
              this.setUser(data);
              this.$router.push({
                name:"profile"
              })
              window.scrollTo(0,0);
            })
            .catch(err => console.log(err))
        }
      },

      setFields(){
        this.username = this.user.username;
        this.name = this.user.name;
        this.phone = this.user.phone;
      }
    },
  created() {
    if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
    this.setFields()
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