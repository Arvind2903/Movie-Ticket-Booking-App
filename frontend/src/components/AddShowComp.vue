<template>
  <div>
    <h1>
      Add a new movie <br>
    </h1>
    <p>
      <strong>
        (* marked fields are important)
      </strong>
    </p>
    <div class="container mt-4">
      <form @submit.prevent="addShow">
        <p style="text-align: left">*Name:</p>
        <input
          type="text"
          class="form-control"
          placeholder="Name of the movie"
          v-model="name">
        <br/>
        <p style="text-align: left">*Date of release:</p>
        <input
          type="date"
          class="form-control"
          v-model="date">
        <br/>
        <p style="text-align: left">*Subtitles (if any):</p>
        <input
          type="text"
          class="form-control"
          placeholder="Subtitle language"
          v-model="subtitles">
        <br/>
        <p style="text-align: left">*Price:</p>
        <input
          type="text"
          class="form-control"
          placeholder="Price of the tickets"
          v-model="price">
        <br/>
        <p style="text-align: left">*Genre:</p>
        <input
          type="text"
          class="form-control"
          placeholder="Main movie genre"
          v-model="genre">
        <br/>
        <p style="text-align: left">*Language of the Movie:</p>
        <input
          type="text"
          class="form-control"
          placeholder="Movie Language"
          v-model="language">
        <br/>
        <p style="text-align: left">*IMDb Rating:</p>
        <input
          type="number"
          step="0.01"
          min="0"
          class="form-control"
          v-model="rating">
        <br/>
        <p style="text-align: left">*Runtime (in minutes):</p>
        <input
          type="number"
          class="form-control"
          v-model="runtime">
        <br/>
        <p style="text-align: left">*Theatres you wish to screen the movie at:</p>
        <div v-for="theatre in theatres" :key="theatre.id">
          <input type="checkbox"
                  id="checkbox"
                  :value=theatre.id
                  v-model="selectedTheatres"/>
          <label for="checkbox"> {{theatre.name}} - {{theatre.max_shows}} Shows in a day
            and {{theatre.total_seats}} seats per screen </label>
        </div>
        <br/>
        <p style="text-align: left">*Add an poster of the movie:</p>
        <input
            type="file"
            accept="image/*"
            class="form-control"
            @change="uploadImage($event)"/>
        <br>
        <div id="preview">
          <img v-if="image.imageUrl"
             :src="image.imageUrl"
             :alt="'Preview Image'"/>
        </div>
        <button
          type="submit"
          class="btn mt-4"
          style="background-image: url(https://cdn-icons-png.flaticon.com/128/3303/3303893.png);
          background-size: 100%; width: 75px; height: 75px">
        </button>
      </form>
      <div v-if="error" class="alert alert-warning alert-dismissible fade show mt-5" role="alert">
        <strong>{{error}}</strong>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data(){
    return{
      name: null,
      date: null,
      subtitles: null,
      price: null,
      genre: null,
      rating: null,
      runtime: null,
      language: null,
      image:{
        image:null,
        imageUrl:null
      },
      error: null,
      theatres: [],
      selectedTheatres: []
    }
  },
  methods:{
    addShow(){
      if(!this.name || !this.date || !this.subtitles || !this.price || !this.genre || !this.rating ||
          !this.runtime || !this.image.image)
        {
          this.error = "Please add all fields"
        }
      else
        {
          let formData = new FormData();
          formData.append('name', this.name);
          formData.append('date', this.date);
          formData.append('subtitles', this.subtitles);
          formData.append('price', this.price);
          formData.append('genre', this.genre);
          formData.append('rating', this.rating);
          formData.append('runtime', this.runtime);
          formData.append('language', this.language);
          formData.append('theatres', this.selectedTheatres);
          formData.append('image', this.image.image, this.image.image.name);
          console.log('adding movie')
          fetch('http://localhost:5000/api/movie',{
          method:"POST",
          headers:{
            "Authentication-Token":this.$store.state.token
          },
            body:formData
        })
            .then(resp => resp.json())
                .then(()=>{
                  this.$router.push({
                    name:"admin"
                  })
                  console.log('added movie');
                  window.scrollTo(0,0);
                })
                .catch(error => console.log(error))
        }
      },
    uploadImage(e){
      const file = e.target.files[0]
      this.image.image = file
      this.image.imageUrl = URL.createObjectURL(file)
      console.log(file)
    },
    getTheatres(){
      fetch('http://localhost:5000/api/theatres',{
          method:"GET",
          headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
          .then(resp => resp.json())
          .then(data => this.theatres.push(...data))
          .catch(error => console.log(error))
    }
  },
  created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
      this.getTheatres()
    }
}
</script>

<style scoped>

</style>