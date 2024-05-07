<template>
  <div>
    <div class="container card-group mt-5">
      <form @submit.prevent="bookTickets">
        <h2 v-if="movie">Booking Tickets for {{movie.name}}</h2><br><br>
        <p style="text-align: left">*Date:</p>
        <input
          type="date"
          id="date"
          class="form-control"
          v-model="date">
        <br/>
        <p style="text-align: left">*Number of seats:</p>
        <input
          type="number"
          class="form-control"
          v-model="number_of_tickets">
        <br/>
        <p style="text-align: left">*Choose the theatre:</p>
        <div v-for="theatre in theatres" :key="theatre.id">
          <input type="radio" :id=theatre.id :value="theatre.id" v-model="selectedTheatre" @change="getTimes(theatre.id, movie_id)">
          <label :for="theatre.id">{{theatre.name}}</label>
        </div>
        <br/>
        <div v-if="selectedTheatre">
          <p style="text-align: left">*Choose the time:</p>
          <div v-for="schedule in times" :key="schedule.id">
            <input type="radio" :id=schedule.id :value="schedule.time" v-model="selectedTime">
            <label :for="schedule.id">{{schedule.time}}</label>
          </div>
        </div>
        <button
            type="submit"
            class="btn mt-4"
            style="background-image: url(https://cdn-icons-png.flaticon.com/128/1834/1834517.png);
            background-size: 100%; width: 80px; height: 80px">
        </button>
        <div v-if="error" class="alert alert-warning alert-dismissible fade show mt-5" role="alert">
        <strong>{{error}}</strong>
      </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data(){
    return{
      date:this.Date,
      number_of_tickets:null,
      theatres:[],
      times:[],
      selectedTheatre: this.theatre,
      selectedTime:this.time,
      error:null,
      movie:null
    }
  },
  props:{
    movie_id:{
      type:[Number, String],
      required:true
    },
    theatre:{
      default:null
    },
    time:{
      default:null
    },
    Date:{
      default:null
    }
  },
  methods:{
    async getTheatres(){
      await fetch(`http://localhost:5000/api/theatres/${this.movie_id}`,{
          method:"PUT",
          headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
          .then(resp => resp.json())
          .then(data => this.theatres.push(...data))
          .catch(error => console.log(error))
    },

    async bookTickets(){
      if(!this.date || !this.number_of_tickets || !this.selectedTheatre || !this.selectedTime){
        this.error = "Please add all required fields"
      }
      else {
        await fetch('http://localhost:5000/api/ticket', {
        method:"POST",
        headers:{
          "Content-Type":"application/json",
          "Authentication-Token":this.$store.state.token
        },
        body:JSON.stringify({date:this.date, number_of_tickets:this.number_of_tickets, time:this.selectedTime,
          theatre_id:this.selectedTheatre, movie_id:this.movie_id})
      })
          .then((response) => {
                if (response.ok){
                  this.$router.push({
                    name:"home"
                  })
                  console.log("Booked Tickets");
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
      },

    getTimes(theatre_id, movie_id){
      if (this.times){
        this.times = []
      }
      fetch(`http://localhost:5000/api/ticket/${theatre_id}/${movie_id}`, {
        method: 'GET',
        headers:{
          "Content-Type":"application/json",
          "Authentication-Token":this.$store.state.token
        }
      })
          .then(resp => resp.json())
          .then(data => this.times.push(...data))
          .catch(error => console.log(error))
    }
  },
    async created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
      await this.getTheatres();
      await fetch(`http://localhost:5000/api/movie/${this.movie_id}`, {
          method:"GET",
          headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
            .then(response => response.json())
            .then(data => {
              this.movie = data;
            })
            .catch(err => console.log(err))
      document.getElementById("date").min = this.Date;
      document.getElementById("date").value = this.Date;
      if (this.theatre && this.time){
        this.getTimes(this.theatre, this.movie_id)
      }

    }
}
</script>

<style scoped>
.card-group{
  margin: 35%;
}
input::placeholder{
  text-align: center;
}
</style>