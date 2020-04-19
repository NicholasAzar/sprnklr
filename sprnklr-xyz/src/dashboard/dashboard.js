import React, {Component} from 'react'
import axios from 'axios'
import Cookies from 'universal-cookie';

const cookies = new Cookies();

export default class Dashboard extends Component {
    state = {
        linked_accounts: [],
        photos: []
    }
    componentDidMount() {
        this.getData();
    }

    async getData() {
        const accounts_response = await axios.get('/api/list-accounts'); 
        console.log("linked accounts? ", accounts_response.data);
        this.setState({linked_accounts: accounts_response.data});

        const photos_response = await axios.get('/api/list-photos');
        console.log('photos response: ', photos_response);
        this.setState({photos: photos_response.data})
    }

    render() {
        return (
            <>
                <h1>Dashboard</h1>
                <p>Logged in as: {cookies.get('user_id')} {cookies.get('acc_type')}</p>
                <h2>Linked Accounts</h2>
                <ul style={{listStyle: "none"}}>
                    {this.state.linked_accounts.map((account) => (
                        <li key={account[0]}>{account[0]}, {account[1]}</li>
                    ))}
                </ul>

                <section>Photos</section>
                <div style={{display: 'flex', flexWrap: 'wrap'}}>
                    {this.state.photos.map((photo) => (
                        <img src={photo.baseUrl} style={{margin: '10px', flex: '1 0 0', height: '200px', objectFit: 'contain'}} key={photo.id}></img>
                    ))}
                    
                </div>
            </>
        )
    }
}


