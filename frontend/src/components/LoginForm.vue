<template>
  <form @submit.prevent="submitLoginForm">
    <div>
      <label for="username">Username</label>
      <input id="username" v-model.trim="$v.loginForm.username.$model" type="text" placeholder="Username">
      <p v-if="!$v.loginForm.username.minLength">Username must be at least 3 characters long</p>
    </div>
    <div>
      <label for="password">Password</label>
      <input id="password" v-model.trim="$v.loginForm.password.$model" type="password" placeholder="Password">
      <p v-if="!$v.loginForm.password.minLength">Password must be at least 8 characters long</p>
      <p v-if="!$v.loginForm.password.containsUppercase">Password must contain at least one uppercase letter</p>
      <p v-if="!$v.loginForm.password.containsNumber">Password must contain at least one number</p>
    </div>
    <div>
      <label>
        <input type="checkbox" v-model="loginForm.remember_me"> Remember Me
      </label>
    </div>
    <button :disabled="$v.loginForm.$invalid" type="submit">Sign In</button>
  </form>
</template>

<script>
import { required, minLength, helpers } from 'vuelidate/lib/validators'
import axios from 'axios';

const containsUppercase = helpers.regex('uppercase', /[A-Z]/)
const containsNumber = helpers.regex('number', /[0-9]/)

export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: '',
        remember_me: false,
      },
    };
  },
  validations: {
    loginForm: {
      username: {
        required,
        minLength: minLength(3)
      },
      password: {
        required,
        minLength: minLength(8),
        containsUppercase,
        containsNumber,
      },
    },
  },
  methods: {
    async submitLoginForm() {
      this.$v.loginForm.$touch();
      if (!this.$v.loginForm.$invalid) {
        try {
          const response = await axios.post('/api/login', this.loginForm);
          // Handle response here
        } catch (error) {
          // Handle error here
        }
      }
    },
  },
};
</script>
