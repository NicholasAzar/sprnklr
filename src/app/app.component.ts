import { Component } from '@angular/core';
import { ClientStoreService } from './client-store/client-store.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Unsubscribable } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'sprnklr';
  private accessToken:string;
  private photosSubscription:Unsubscribable;

  constructor(private clientStore: ClientStoreService, private http:HttpClient) {
    this.accessToken = this.clientStore.get('accessToken');
    console.log("accessToken: ", this.accessToken);
  }

  sendRequest() {
    this.photosSubscription = this.http.get('https://photoslibrary.googleapis.com/v1/mediaItems', {headers: new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + this.accessToken
    })})
    .subscribe((result) => {
      console.log("Result: ", result);
    })
  }

  ngOnDestroy() {
    if (this.photosSubscription) {
      this.photosSubscription.unsubscribe();
    }
  }
}
