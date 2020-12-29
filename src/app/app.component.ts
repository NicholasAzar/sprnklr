import { Component } from '@angular/core';
import { ClientStoreService } from './client-store/client-store.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'sprnklr';

  constructor(private clientStore: ClientStoreService) {
    console.log("accessToken: ", this.clientStore.get('accessToken'));
  }
}
