<template>
  <div style="padding-top: 20px">
    <div id="manage">
      <div class="grouping">
        <div class="groupLabel">
          <h2>Theatres managed by you</h2>
          <div v-for="theatre in theatres" :key="theatre.id">
            <router-link :to="{name:'theatre', params:{theatre_id:theatre.id}}" class="text-style btn theatre" tag="button">
              <h4>{{theatre.name}}</h4>
            </router-link>
          </div>
        </div>
      </div>
      <div class="grouping">
        <div class="groupLabel">
          <h2>Movies managed by you</h2>
          <div v-for="movie in movies" :key="movie.id">
            <router-link :to="{name:'movie', params:{movie_id:movie.id}}" class="text-style btn theatre" tag="button">
              <h4>{{movie.name}}</h4>
            </router-link>
          </div>
        </div>
      </div>
    </div>
    <hr>
    <div id="create">
      <div class="grouping">
        <button
          @click="addTheatre"
          id="theatre"
          class="btn btn-group mt-4"
          style="background-image: url(https://cdn-icons-png.flaticon.com/128/1778/1778517.png);
          background-size: 100%; width: 75px; height: 75px; margin-left: 10px; background-repeat:
          no-repeat; background-clip: padding-box;">
        </button>
        <label for="theatre" class="groupLabel"><h3>Add a new theatre</h3></label>
      </div>
      <div class="grouping">
        <button
            @click="addShow"
            id="movie"
            class="btn btn-group mt-4"
            style="background-image: url(https://cdn-icons-png.flaticon.com/128/1179/1179120.png);
            background-size: 100%; width: 75px; height: 75px; margin-left: 10px; background-repeat:
          no-repeat; background-clip: padding-box;">
        </button>
        <label for="movie" class="groupLabel"><h3>Add a new movie</h3></label>
      </div>
    </div>
    <hr>
  </div>
</template>

<script>
export default {
  data(){
    return{
      theatres:[],
      movies:[]
    }
  },
  methods:{
    addTheatre(){
      this.$router.push({
        name: 'addTheatre'
      })
      console.log('adding theatre');
      window.scrollTo(0,0);
    },

    addShow(){
      this.$router.push({
        name: 'addShow'
      })
      console.log('adding show');
      window.scrollTo(0,0);
    },

    getTheatres(){
      fetch('http://localhost:5000/api/theatres',{
          method:"POST",
          headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
          .then(resp => resp.json())
          .then(data => this.theatres.push(...data))
          .catch(error => console.log(error))
    },

    getMovies(){
      fetch('http://localhost:5000/api/movies',{
          method:"POST",
          headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
          .then(resp => resp.json())
          .then(data => this.movies.push(...data))
          .catch(error => console.log(error))
    }
  },
  created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
      }
      this.getTheatres();
      this.getMovies();
    }
}
</script>

<style scoped>
.grouping{
  display: inline-block;
  text-align: center;
  float: top;
  vertical-align: top;
}

.groupLabel{
  display: block;
  margin-right: 50px;
}
</style>