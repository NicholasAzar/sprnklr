import { Component } from '@angular/core';
import {AuthService} from './auth/auth.service';

const Store = (<any>window).require('electron-store');

const store = new Store();

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'sprnklr';

  constructor(private authService: AuthService) {
    console.log("accessToken: ", store.get('accessToken'));
  }
}
