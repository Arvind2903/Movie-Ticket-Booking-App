<template>
<div style="padding-top: 30px">
  <div id="search">
    <div style="margin-left: 50px; margin-right:50px; display:inline-block">
      <input style="width: min-content"
             class="form-control"
             type="text"
             id="byName"
             placeholder="Search Movie"
             v-model="searchName"><br>
      <select id="movieList" v-if="names" class="form-control form-select"
            v-on:change="changeRoute($event)">
          <option id="defaultMovie">---Click to view Movies---</option>
          <option v-if="(nameSearch).length===0" selected disabled>
            No movies found
          </option>
          <option v-for="obj in nameSearch"
                  :key="obj.id"
                  :value="obj.id">
            {{obj.name}}
          </option>
      </select>
    </div>
    <div style="margin-left: 50px; margin-right:50px; display:inline-block" id="byRatings">
      <label for="byRatings"><h4>Filter Movies by Rating</h4></label><br><br>
      <div style="margin-left: 50px; margin-right:50px; display:inline-block;">
        <label for="minRating"><h6>Minimum Rating</h6></label>
        <input style="width: min-content"
               class="form-control"
               type="number"
               step="0.01"
               min="0"
               max="10"
               id="minRating"
               @change="ratingsReload($event)"
               v-model="minRating">
      </div>
    </div>
    <div style="margin-left: 50px; margin-right:50px; display:inline-block">
      <input style="width: min-content"
             class="form-control"
             type="text"
             id="byGenre"
             placeholder="Search Genre"
             v-model="searchGenre"><br>
      <select id="genreList" v-if="genres" class="form-control form-select"
            v-on:change="genreReload($event)">;
          <option id="defaultGenre" value="all">---Click to view Genres---</option>
          <option v-if="(genreSearch).length===0" selected disabled>
            No genres found
          </option>
          <option v-for="genre in genreSearch"
                  :key="genre"
                  :value="genre">
            {{genre}}
          </option>
      </select>
    </div>
    <div style="margin-left: 50px; margin-right:50px; display:inline-block">
      <input style="width: min-content"
             class="form-control"
             type="text"
             id="byLanguage"
             placeholder="Search Language"
             v-model="searchLanguage"><br>
      <select id="languageList" v-if="languages" class="form-control form-select" v-on:change="languageReload($event)">
          <option value="all">---Click to view Languages---</option>
          <option v-if="(languageSearch).length===0" selected disabled>
            No languages found
          </option>
          <option v-for="language in languageSearch"
                  :key="language"
                  :value="language">
            {{language}}
          </option>
      </select>
    </div>
  </div>
  <hr>
  <div id="movies">
    <div v-for="movie in movies" :key="movie.id">
      <img :src="require('../assets/images/' + `${movie.name}` + '.png')"
           :alt="'Image of post ' + `${movie.name}`"
           style="width: 20%; height: 20%">
      <br>
      <router-link :to="{name:'movie', params:{movie_id:movie.id}}"
                     class="btn"
                     tag="button">
          <h3>{{movie.name}}</h3>
        </router-link><br><br>
      <div style="margin-right: 15px">
          <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">Subs: {{movie.subtitles}}</h5>
          <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">Language: {{movie.language}}</h5>
          <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">IMDb: {{movie.rating}}</h5>
        </div><br>
      <div style="margin-right: 15px">
          <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">Price: &#8377; {{movie.price}}</h5>
          <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">Genre: {{movie.genre}}</h5>
          <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">Runtime: {{movie.runtime}}</h5>
        </div><br>
      <router-link id="book"
                   :to="{name:'booking', params:{movie_id:movie.id, Date:getMinDate(movie.date)}}"
                   class="text-style btn book" tag="button"></router-link>
      <label for="book">Book Tickets</label>
      <hr>
    </div>
  </div>
</div>
</template>

<script>
export default {
  data(){
    return{
      allMovies:[],
      movies:[],
      names:[],
      genres:[],
      languages:[],
      searchName:"",
      searchGenre:"",
      searchLanguage:"",
      minRating:0
    }
  },
  methods:{
    async getMovies(){
      await fetch('http://localhost:5000/api/movies',{
          method:"PUT",
          headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
          .then(resp => resp.json())
          .then(data => this.allMovies.push(...data))
          .catch(error => console.log(error))
    },

    getFilters(){
      this.names = this.allMovies.map(({id,name}) => ({id,name}));
      function onlyUnique(value, index, array) {
          return array.indexOf(value) === index;
        }

      this.genres = (this.allMovies.map(obj => obj.genre)).filter(onlyUnique);
      this.languages = (this.allMovies.map(obj => obj.language)).filter(onlyUnique);
    },

    getMinDate(movie_date){
      const date = new Date()
      const offset = date.getTimezoneOffset()
      const todayDate = new Date(date.getTime() - (offset*60*1000))
      let minDate = null;
      if (todayDate.toISOString().split('T')[0] > movie_date){
        minDate = todayDate.toISOString().split('T')[0];
      }
      else{
        minDate = movie_date;
      }
      return minDate;
    },

    changeRoute(e){
      this.$router.push({
        name:"movie",
        params:{
          movie_id:e.target.value
        }
      })
      window.scrollTo(0,0);
    },

    genreReload(e){
      const genre = e.target.value;
      if (genre==='all'){
        this.movies = this.allMovies;
      }
      else{
        this.movies = this.allMovies.filter(obj => {
          return obj.genre===genre;
      })
      }
    },

    languageReload(e){
      const language = e.target.value;
      if (language==='all'){
        this.movies = this.allMovies;
      }
      else{
        this.movies = this.allMovies.filter(obj => {
          return obj.language===language;
      })
      }
    },

    ratingsReload(e){
      const minRating = e.target.value;
      this.movies = this.allMovies.filter(obj => {
        return parseInt(obj.rating) >= parseInt(minRating);
      })
    }
  },
  computed:{
    nameSearch(){
      return this.names.filter(p =>{
        return p.name.toLowerCase().indexOf(this.searchName.toLowerCase()) !== -1;
      })
    },
    genreSearch(){
      return this.genres.filter(p =>{
        return p.toLowerCase().indexOf(this.searchGenre.toLowerCase()) === 0;
      })
    },
    languageSearch(){
      return this.languages.filter(p =>{
        return p.toLowerCase().indexOf(this.searchLanguage.toLowerCase()) === 0;
      })
    }
  },
  async created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
      }
        await this.getMovies();
        this.movies = this.allMovies.reverse();
        await this.getFilters();
    }
}
</script>

<style scoped>
.book{
  width: 75px;
  height: 72px;
  background-image: url(https://cdn-icons-png.flaticon.com/128/5576/5576915.png);
  background-size: 100%;
  background-repeat: no-repeat;
  background-clip: border-box;
}
</style>