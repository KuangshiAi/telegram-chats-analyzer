import React from 'react';
import TelegramIcon from '@mui/icons-material/Telegram';

export default function Header(props) {

    return (
        <header className="App-header">
            <h1 className="text-warning" ><TelegramIcon sx={{ fontSize: 60 }} color="primary" />Telegram Chats Analyzer</h1> 
            <button type="button" className="btn btn-success btn-lg opacity-75" onClick={props.onClick}>
                START
            </button>
        </header>
    )
}