<template>
  <div>
    <div v-if="movie">
      <div class="date" style="background-color: lightcoral">
        <h3><label for="date">Choose the Date</label>&nbsp;</h3>
        <input
            type="date"
            @change="getBookedSeats"
            v-model="date"
            id="date">
      </div>
      <h1 class="mt-3">{{movie.name}}</h1><br>
      <img :src="require('../assets/images/' + `${movie.name}` + '.png')"
           :alt="'Image of post ' + `${movie.name}`"
            style="width: 10%; height: 10%">
        <br><br>
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
      <div v-if="user.admin && (movie.user_id === user.id)">
        <router-link :to="{name:'editShow', params:{movie_id:movie.id}}" class="text-style editt btn" tag="button"></router-link>&nbsp;&nbsp;
        <button class="remove btn" @click="deleteMovie"></button>
      </div>
      <hr>
      <div v-for="obj in array" :key="obj.id" class="movie">
        <router-link :to="{name:'theatre', params:{theatre_id:obj.id}}"
                     class="btn book"
                     tag="button">
          <h3>{{obj.name}}</h3>
        </router-link><br>
        <h5>{{obj.address}}</h5>
        <div v-if="seats">
          <div v-for="schedule in schedules.filter(Z => {return Z['id'] === obj.id})"
               :key="schedule.id"
               style="margin-left: 10px"
               id="shows">
            <div v-for="(value, key, index) in seats[schedule.id]" :key="key">
              <router-link :id="index"
                     :to="{name:'booking', params:{
                       movie_id: movie_id,
                      theatre: schedule.id,
                      time: key,
                      Date: date}}"
                     class="btn btn-outline-primary" tag="button">
              {{key}}
            </router-link>&nbsp;
              <label :for="index">Number of seats left: {{value}}</label>
            </div>
          </div>
        </div>
        <hr>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data(){
    return{
      movie:null,
      schedules:[],
      array:{},
      theatre_ids:[],
      date:null,
      seats:null,
      calendar:{
        min:null,
        value:null
      },
      user:this.$store.state.user
    }
  },
  methods:{
    async getMovieSchedules() {

      await fetch(`http://localhost:5000/api/movie/${this.movie_id}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": this.$store.state.token
        }
      })
          .then(resp => resp.json())
          .then(data => {
            this.movie = data;
          })
          .catch(error => console.log(error))

      let theatre_ids = []
      await fetch(`http://localhost:5000/api/theatres/${this.movie_id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          }
        })
            .then(resp => resp.json())
            .then(data => {
              this.schedules.push(...data);
              theatre_ids.push(...this.schedules.map(obj => {
                return obj.id
              }));
              console.log(theatre_ids);
              theatre_ids = [...new Set(theatre_ids)]
            })
            .catch(error => console.log(error))

      this.theatre_ids = theatre_ids;
      let array = {};
      for (let theatre_id in theatre_ids){
        await fetch(`http://localhost:5000/api/theatre/${theatre_ids[theatre_id]}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          }
        })
            .then(resp => resp.json())
            .then(data => {
              let key = theatre_ids[theatre_id]
              array[key] = data;
            })
            .catch(error => console.log(error))
        }
      this.array = array;
    },

    getBookedSeats(){
      fetch(`http://localhost:5000/api/movie-seats/${this.movie_id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          },
        body:JSON.stringify({'date':this.date, 'times':this.schedules.map(obj => obj.time), 'theatre_ids':this.theatre_ids})
        })
            .then(resp => resp.json())
            .then(data => {
              this.seats = data;
            })
            .catch(error => console.log(error))
    },

    deleteMovie(){
      const confirmation = confirm('Are you sure you want to remove this movie? This action is irreversible')
      if (confirmation){
         fetch(`http://localhost:5000/api/movie/${this.movie_id}`, {
          method: "DELETE",
          headers: {
              "Content-Type": "application/json",
              "Authentication-Token": this.$store.state.token
            }
        })
            .then(resp => resp.json())
            .then(() => {
              console.log('Deleted Movie Successfully');
              this.$router.push({
                  name:"profile"
                })
              window.scrollTo(0,0);
            })
            .catch(error => console.log(error))
      }
    }
  },
  props:{
    movie_id:{
      type:[Number, String],
      required: true
    }
  },
  async created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
      await this.getMovieSchedules();
      const date = new Date()
      const offset = date.getTimezoneOffset()
      const todayDate = new Date(date.getTime() - (offset*60*1000))
      let minDate = null;
      if (todayDate.toISOString().split('T')[0] > this.movie.date){
        minDate = todayDate.toISOString().split('T')[0];
      }
      else{
        minDate = this.movie.date;
      }
      this.date = minDate
      document.getElementById("date").min = minDate;
      document.getElementById("date").value = minDate;
      console.log('filled calendar')
      await fetch(`http://localhost:5000/api/movie-seats/${this.movie_id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          },
        body:JSON.stringify({'date':this.date, 'theatre_ids':this.theatre_ids})
        })
            .then(resp => resp.json())
            .then(data => {
              this.seats = data;
            })
            .catch(error => console.log(error))
    }
}
</script>

<style scoped>
.date{
  float:right;
  margin-left: 1000px;
  margin-top: 50px;
  position: absolute;
}
.editt{
  background-image: url(https://cdn-icons-png.flaticon.com/128/1828/1828911.png);
  width: 20px;
  height: 30px;
  background-size: 100%;
  background-repeat: no-repeat;
  background-clip: border-box;
}
.remove{
  background-image: url(https://cdn-icons-png.flaticon.com/128/484/484611.png);
  width: 20px;
  height: 30px;
  background-size: 100%;
  background-repeat: no-repeat;
  background-clip: border-box;
}
.text-style{
  text-align: left !important;
  font-size:30px;
  text-decoration: none !important;
  font-family: fantasy !important;
  color: floralwhite !important;
}
</style>