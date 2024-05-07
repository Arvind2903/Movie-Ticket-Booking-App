<template>
  <div>
    <h1> Welcome to your profile, {{user.username}}</h1>
    <br>
    <div>
      <div style="float: left; display: inline-block; margin-left: 750px; margin-bottom: -60px">
        <router-link to="/edit-profile" class="text-style btn editt" tag="button"></router-link>
      </div>
      <br>
      <div style="float: right; display: inline-block; margin-right: 750px; margin-top: -17px">
        <button class="btn remove" @click="deleteUser"></button>
      </div>
      <br>
    </div>
    <br><br><br>
    <div v-if="user">
      <div v-for="(value,key,index) in user" :key="index">
        <div v-if="key==='email' || key==='name' || key==='phone' || key==='username'">
          <div style="float: left; display: inline-block; margin-left: 550px">
            <h5 style="text-transform: capitalize"><b>{{key}}</b>:</h5>
          </div>
          <div style="float: right; display: inline-block; margin-right: 550px">
            <h5>{{value}}</h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data(){
    return{
      user: this.$store.state.user
    }
  },
  methods:{
    async deleteUser(){
      const confirmDelete = confirm("Are you sure you want to delete your account? This action is irreversible!")
      if(confirmDelete){
        await fetch("http://localhost:5000/api/user", {
        method:"DELETE",
        headers:{
          "Content-Type":"application/json",
          "Authentication-Token":this.$store.state.token
        }
      })
          .then(resp => resp.json())
          .catch(err => console.log(err))

      await this.$router.push({
          name:"login"
        })
        window.scrollTo(0,0);
      }
    }
  },
  created() {
    if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
    }
}
</script>

<style scoped>
.editt{
  background-image: url(https://cdn-icons-png.flaticon.com/128/8188/8188360.png);
  width: 60px;
  height: 60px;
  background-size: 100%;
  background-repeat: no-repeat;
  background-clip: border-box;
}
.remove{
  background-image: url(https://cdn-icons-png.flaticon.com/128/8867/8867478.png);
  width: 50px;
  height: 50px;
  background-size: 100%;
  background-repeat: no-repeat;
  background-clip: border-box;
}
</style>