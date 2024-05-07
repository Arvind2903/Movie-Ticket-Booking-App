<template>
  <div>
    <div v-if="theatre">
      <div class="date" style="background-color: lightcoral">
        <h3><label for="date">Choose the Date</label>&nbsp;</h3>
        <input
            type="date"
            @change="getBookedSeats"
            v-model="date"
            id="date">
      </div>
      <h1 class="mt-3">{{theatre.name}}</h1>
      <h4 class="mt-3">
        {{theatre.address}}
      </h4>
      <br>
      <div v-if="user.admin && (theatre.user_id===user.id)">
        <router-link :to="{name:'editTheatre', params:{theatre_id:theatre.id}}" class="editt btn" tag="button"></router-link>&nbsp;&nbsp;
        <button class="remove btn" @click="deleteTheatre"></button>
        <div id="export">
          <button
                @click="exportData"
                id="export"
                class="btn btn-group mt-4"
                style="background-image: url(https://cdn-icons-png.flaticon.com/128/3405/3405255.png);
                background-size: 100%; width: 40px; height: 40px; margin-left: 10px; background-repeat:
              no-repeat; background-clip: padding-box;">
            </button>
          <br>
            <label for="export" class="groupLabel"><h4>Export Data</h4></label>
        </div>
      </div>
      <hr>
      <div v-for="obj in array" :key="obj.id" class="movie">
        <div v-if="date>=obj.date">
          <router-link :to="{name:'movie', params:{movie_id:obj.id}}"
                     class="btn book"
                     tag="button">
          <h3>{{obj.name}}</h3>
          </router-link><br>
          <div style="margin-right: 15px">
            <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">Subs: {{obj.subtitles}}</h5>
            <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">{{obj.language}}</h5>
            <h5 style="margin-left: 50px; margin-right:50px; display:inline-block">IMDb: {{obj.rating}}</h5>
          </div><br>
          <img :src="require('../assets/images/' + `${obj.name}` + '.png')"
             :alt="'Image of post ' + `${obj.name}`"
              style="width: 10%; height: 10%">
          <br>
          <div v-if="seats">
            <div v-for="schedule in schedules.filter(Z => {return Z['movie_id'] === obj.id})"
                 :key="schedule.id"
                 style="margin-left: 10px"
                 id="shows">
              <router-link id="book"
                       :to="{name:'booking', params:{
                         movie_id: schedule.movie_id,
                        theatre: theatre_id,
                        time: schedule.time,
                        Date: date}}"
                       class="btn btn-outline-primary" tag="button">
                {{schedule.time}}
              </router-link>&nbsp;
              <label for="shows">Number of seats left: {{seats[schedule.movie_id][schedule.time]}}</label>
            </div>
          </div>
          <hr>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data(){
    return{
      theatre:null,
      schedules:[],
      array:{},
      movie_ids:[],
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

      await fetch(`http://localhost:5000/api/theatre/${this.theatre_id}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          }
        })
            .then(resp => resp.json())
            .then(data => {
              this.theatre = data;
            })
            .catch(error => console.log(error))

      let movie_ids = []
        await fetch(`http://localhost:5000/api/movies/${this.theatre_id}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          }
        })
            .then(resp => resp.json())
            .then(data => {
              this.schedules.push(...data);
              movie_ids.push(...this.schedules.map(obj => {
                return obj.movie_id
              }));
              movie_ids = [...new Set(movie_ids)]
            })
            .catch(error => console.log(error))

      this.movie_ids = movie_ids;
      let array = {};
      for (let movie_id in movie_ids){
        await fetch(`http://localhost:5000/api/movie/${movie_ids[movie_id]}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          }
        })
            .then(resp => resp.json())
            .then(data => {
              let key = movie_ids[movie_id]
              array[key] = data;
            })
            .catch(error => console.log(error))
        }
      console.log('Obtained show data');
      this.array = array
      },

    getBookedSeats(){
      fetch(`http://localhost:5000/api/theatre-seats/${this.theatre_id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          },
        body:JSON.stringify({'date':this.date, 'times':this.schedules.map(obj => obj.time), 'movie_ids':this.movie_ids})
        })
            .then(resp => resp.json())
            .then(data => {
              this.seats = data;
              console.log(data);
            })
            .catch(error => console.log(error))
    },
    deleteTheatre(){
      const confirmation = confirm('Are you sure you want to remove this theatre? This action is irreversible')
      if (confirmation){
         fetch(`http://localhost:5000/api/theatre/${this.theatre_id}`, {
          method: "DELETE",
          headers: {
              "Content-Type": "application/json",
              "Authentication-Token": this.$store.state.token
            }
        })
            .then(resp => resp.json())
            .then(() => {
              console.log('Deleted Theatre Successfully');
              this.$router.push({
                  name:"profile"
                })
              window.scrollTo(0,0);
            })
            .catch(error => console.log(error))
      }
    },
    exportData(){
      fetch(`http://localhost:5000/api/export/${this.theatre_id}`,{
        method: 'GET',
        headers: {
              "Content-Type": "application/json",
              "Authentication-Token": this.$store.state.token
            }
      })
          .then(resp => resp.json())
          .then(() =>{
            console.log('Exported Data Successfully');
            alert("Check your email for the requested details!")
          })
    }
  },
  props:{
    theatre_id: {
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
      this.calendar.min = todayDate.toISOString().split('T')[0];
      this.calendar.value = todayDate.toISOString().split('T')[0];
      document.getElementById('date').min = this.calendar.min;
      document.getElementById('date').value = this.calendar.value;
      this.date = this.calendar.value;
      console.log('filled calendar')
      await fetch(`http://localhost:5000/api/theatre-seats/${this.theatre_id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": this.$store.state.token
          },
        body:JSON.stringify({'date':this.date, 'times':this.schedules.map(obj => obj.time), 'movie_ids':this.movie_ids})
        })
            .then(resp => resp.json())
            .then(data => {
              this.seats = data;
              console.log(data);
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
</style>