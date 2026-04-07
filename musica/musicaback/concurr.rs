// This will be primarily for API concurrency
// We'll be using a concurrecy for this endeavor, so we can have high speed, 
// we'll be able to sustain many API calls to sustain many many users

//  MAIN system for the API calls
extern crate requests;
use requests::ToJson;

fn main():
    // This is where we would make the API calls, and then we would use the data to create a mix playlist for the user.
    // We're able to generaete like a mixed playlist or even compare if they're compaitable 
    // We're using soundchart APi for this endeavor
    
    // We would also be able to use the data to create a mix playlist for the user, and then we would be able to compare if they're compaitable
    let request_deezer = requests::get("https://api.deezer.com/search/artist");
