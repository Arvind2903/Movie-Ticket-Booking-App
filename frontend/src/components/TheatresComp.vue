<template>
<div>
  <div id="search">
    <div style="margin-left: 50px; margin-right:50px; display:inline-block">
      <label for="byAddress">Search by Theatre</label>
      <input style="width: min-content" autofocus
             class="form-control"
             type="text"
             id="byTheatre"
             placeholder="Search Theatre"
             v-model="searchName"><br>
      <select id="theatreList" v-if="names" class="form-control form-select" v-on:change="changeRoute($event)">
          <option id="defaultTheatre">---Click to view Theatres---</option>
          <option v-if="(nameSearch).length===0" selected disabled>
            No Theatres found
          </option>
          <option v-for="obj in nameSearch"
                  :key="obj.id"
                  :value="obj.id">
            {{obj.name}}
          </option>
      </select>
    </div>
    <div style="margin-left: 50px; margin-right:50px; display:inline-block">
      <label for="byAddress">Search by Location</label>
      <input style="width: min-content"
             class="form-control"
             type="text"
             id="byAddress"
             @change="reloadLocation"
             placeholder="Search"
             v-model="searchAddress"><br>
    </div>
  </div>
  <hr>
  <div id="theatres">
    <div v-for="theatre in theatres" :key="theatre.id">
      <h1 class="mt-3">
        <router-link :to="{name:'theatre', params:{theatre_id:theatre.id}}" class="text-style btn theatre" tag="button">
          {{theatre.name}}
        </router-link>
      </h1>
      <h4 class="mt-3">
        {{theatre.address}}
      </h4>
      <img :src="require('../assets/images/' + `${theatre.name}` + '.png')"
           :alt="'Image of post ' + `${theatre.name}`"
           style="width: 50%; height: 50%">
      <div style="margin-right: 15px">
        <img v-if="theatre.fnb" src="https://cdn-icons-png.flaticon.com/128/685/685352.png" alt="fnb" class="addons">
        <img v-if="theatre.wheelchair" src="https://cdn-icons-png.flaticon.com/128/93/93191.png" alt="wheelchair" class="addons">
        <img v-if="theatre.parking" src="https://cdn-icons-png.flaticon.com/128/414/414609.png" alt="parking" class="addons">
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
      theatres:[],
      names:[],
      allTheatres:[],
      searchAddress:"",
      searchName:""
    }
  },
  methods:{
    async getTheatres(){
      await fetch('http://localhost:5000/api/theatres',{
          method:"GET",
          headers:{
            "Content-Type":"application/json",
            "Authentication-Token":this.$store.state.token
          }
        })
          .then(resp => resp.json())
          .then(data => this.allTheatres.push(...data))
          .catch(error => console.log(error))
    },

    reloadLocation(){
      this.theatres = this.allTheatres.filter(p =>{
        return p.address.toLowerCase().indexOf(this.searchAddress.toLowerCase()) !== -1
      })
    },

    changeRoute(e){
      console.log(e.target.value);
      this.$router.push({
        name:"theatre",
        params:{
          theatre_id:e.target.value
        }
      })
      window.scrollTo(0,0);
    },

    getFilters(){
      this.names = this.allTheatres.map(({id,name}) => ({id,name}));
    }
  },
  computed:{
    nameSearch(){
      return this.names.filter(p =>{
        return p.name.toLowerCase().indexOf(this.searchName.toLowerCase()) !== -1;
      })
    }
  },
  async created(){
      if (!(this.user)){
        this.$store.state.user = JSON.parse(localStorage['user'])
        this.$store.state.token = localStorage['token']
        this.user = this.$store.state.user
      }
      await this.getTheatres();
      this.theatres = this.allTheatres;
      await this.getFilters();
    }

}
</script>

<style scoped>
.theatre{
  width: 300px;
  height: 72px;
  font-size: larger;
}
.theatre:hover{
  color:grey;
  text-decoration: none;
}
.addons{
  margin-left: 50px;
  margin-right:50px;
  display:inline-block;
  width: 50px;
  height: 50px;
}
#byAddress::placeholder{
  text-align: center;
}
#byTheatre::placeholder{
  text-align: center;
}
</style>