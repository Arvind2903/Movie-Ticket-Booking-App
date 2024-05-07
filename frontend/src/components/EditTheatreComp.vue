<template>
  <div>
    <h1>
      Add a new theatre
    </h1>
    <p>
      <strong>
        (* marked fields are important)
      </strong>
    </p>
    <div class="container mt-4">
      <form @submit.prevent="editTheatre">
        <p style="text-align: left">*Name:</p>
        <input
          type="text"
          class="form-control"
          placeholder="Name of the theatre"
          v-model="name">
        <br/>
        <p style="text-align: left">*Address:</p>
        <textarea
            rows="3"
            class="form-control"
            placeholder="Please enter the address of the theatre"
            v-model="address">
        </textarea>
        <br/>
        <p style="text-align: left">*Is there support for people who use wheelchairs?</p>
        <input type="checkbox"
               id="checkbox"
               v-model="wheelchair" />
        <label for="checkbox">{{ wheelchair ? 'Yes' : 'No' }}</label>
        <br/><br/>
        <p style="text-align: left">*Does the theatre have a designated parking lot?</p>
        <input type="checkbox"
               id="checkbox"
               v-model="parking" />
        <label for="checkbox">{{ parking ? 'Yes' : 'No' }}</label>
        <br/><br/>
        <p style="text-align: left">*Does the theatre have food and beverages?</p>
        <input type="checkbox"
               id="checkbox"
               v-model="fnb" />
        <label for="checkbox">{{ fnb ? 'Yes' : 'No' }}</label>
        <br/><br/>
        <p style="text-align: left">*Total Number of seats per screen:</p>
        <input
          type="number"
          class="form-control"
          placeholder="Please enter the total number of seats available"
          v-model="total_seats">
        <br/><br/>
        <p style="text-align: left">*Add an image of the theatre:</p>
        <input
            type="file"
            accept="image/*"
            class="form-control"
            @change="uploadImage($event)"/>
        <div id="preview">
          <img v-if="image.imageUrl"
             :src="image.imageUrl"
             :alt="'Preview Image'"/>
        </div>
        <button
          type="submit"
          class="btn mt-4"
          style="background-image: url(https://cdn-icons-png.flaticon.com/128/3097/3097412.png);
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
      theatre:null,
      name: null,
      address: null,
      wheelchair: false,
      parking: false,
      fnb: false,
      total_seats:null,
      image:{
        image:null,
        imageUrl:null
      },
      error: null
    }
  },
  methods:{
    editTheatre(){
      if(!this.name || !this.address  || !this.max_shows || !this.total_seats)
        {
          this.error = "Please add all fields"
        }
      else
        {
          let formData = new FormData();
          formData.append('name', this.name);
          formData.append('address', this.address);
          formData.append('wheelchair', this.wheelchair);
          formData.append('parking', this.parking);
          formData.append('fnb', this.fnb);
          formData.append('total_seats', this.total_seats);
          if (this.image.image){
            formData.append('image', this.image.image, this.image.image.name);
          }
          fetch(`http://localhost:5000/api/theatre/${this.theatre_id}`, {
            method:"PUT",
            headers:{
                "Authentication-Token":this.$store.state.token
              },
                body:formData
            })
                .then(resp => resp.json())
                    .then(()=>{
                      console.log('Edited Theatre Successfully')
                      this.$router.push({
                        name:"theatre",
                        params:{
                          theatre_id: this.theatre_id
                        }
                      })
                      window.scrollTo(0,0);
                    })
                    .catch(error => console.log(error))
        }},
    uploadImage(e){
      const file = e.target.files[0]
      this.image.image = file
      this.image.imageUrl = URL.createObjectURL(file)
      console.log(file)
    },
    setFields(){
      this.name = this.theatre.name;
      this.address = this.theatre.address;
      this.parking = this.theatre.parking;
      this.fnb = this.theatre.fnb;
      this.total_seats = this.theatre.total_seats;
    }

  },
  props:{
    theatre_id:{
      type:[Number, String],
      required:true
    }
  },
  async created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
      await fetch(`http://localhost:5000/api/theatre/${this.theatre_id}`, {
        method:"GET",
        headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
            .then(response => response.json())
            .then(data => {
              this.theatre = data;
            })
            .catch(err => console.log(err))

      await this.setFields();
    }
}
</script>

<style scoped>

</style>