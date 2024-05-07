<template>
  <div style="padding-top: 10px">
    <div style="float:left; margin-left: 500px">
      <router-link id="movies" to="/movies" class="text-style btn movies grouping" tag="button"></router-link>
      <h1><label for="movies" class="groupLabel">Browse Movies</label></h1>
    </div>
    <div style="float: right; margin-right: 500px">
      <router-link id="theatres" to="/theatres" class="text-style btn theatres grouping" tag="button"></router-link>
      <h1><label for="theatres" class="groupLabel">Browse Theatres</label></h1>
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
.movies{
  width: 200px;
  height: 200px;
  background-image: url(https://cdn-icons-png.flaticon.com/128/3163/3163508.png);
  background-size: 100%;
  background-repeat: no-repeat;
  background-clip: padding-box;
}
.theatres{
  width: 200px;
  height: 200px;
  background-image: url(https://cdn-icons-png.flaticon.com/128/2061/2061094.png);
  background-size: 100%;
  background-repeat: no-repeat;
  background-clip: padding-box;
}
.grouping{
  display: inline-block;
  text-align: center;
  vertical-align: top;
}

.groupLabel{
  display: block;
  margin-right: 50px;
}
</style>