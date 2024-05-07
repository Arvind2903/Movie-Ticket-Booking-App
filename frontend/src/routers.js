import VueRouter from 'vue-router'
import Vue from "vue";
import LoginComp from "@/components/LoginComp";
import HomeComp from "@/components/HomeComp";
import SignupComp from "@/components/SignupComp";
import UserProfileComp from "@/components/UserProfileComp";
import AdminComp from "@/components/AdminComp";
import AddTheatreComp from "@/components/AddTheatreComp";
import AddShowComp from "@/components/AddShowComp";
import MoviesComp from "@/components/MoviesComp";
import BookingComp from "@/components/BookingComp";
import TheatresComp from "@/components/TheatresComp";
import EditTheatreComp from "@/components/EditTheatreComp";
import EditShowComp from "@/components/EditShowComp";
import TheatreComp from "@/components/TheatreComp";
import MovieComp from "@/components/MovieComp";
import EditProfileComp from "@/components/EditProfileComp";

Vue.use(VueRouter)
const routes = [
    {
        path:'/',
        name:'login',
        component:LoginComp,
        meta:{
            hideNavbar: true
        }
    },
    {
        path:'/home',
        name:'home',
        component:HomeComp,
    },
    {
        path:'/signup',
        name:'signup',
        component:SignupComp,
        meta:{
            hideNavbar: true
        }
    },
    {
        path:'/profile',
        name:'profile',
        component:UserProfileComp,
    },
    {
        path:'/admin',
        name:'admin',
        component:AdminComp,
    },
    {
        path:'/add-theatre',
        name:'addTheatre',
        component:AddTheatreComp,
    },
    {
        path:'/add-show',
        name:'addShow',
        component:AddShowComp,
    },
    {
        path:'/movies',
        name:'movies',
        component:MoviesComp,
    },
    {
        path:'/theatres',
        name:'theatres',
        component:TheatresComp,
    },
    {
        path:'/booking/:movie_id',
        name:'booking',
        component:BookingComp,
        props:true
    },
    {
        path:'/edit-theatre/:theatre_id',
        name:'editTheatre',
        component:EditTheatreComp,
        props:true
    },
    {
        path:'/edit-show/:movie_id',
        name:'editShow',
        component:EditShowComp,
        props:true
    },
    {
        path:'/edit-profile',
        name:'editProfile',
        component:EditProfileComp,
    },
    {
        path:'/theatre/:theatre_id',
        name:'theatre',
        component:TheatreComp,
        props:true
    },
    {
        path:'/movie/:movie_id',
        name:'movie',
        component:MovieComp,
        props:true
    }
]

const router = new VueRouter({
    routes
})

export default router