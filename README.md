# AKB48WorldCalc
## Intro
This is a coding project I did in Jan 2022. After that, I do not update it regarding on game mechanism.(and I have not played the game ever since). It supposed to be my final project of CS50. Frankly speaking, I was hesitate to publish it since it is very immature in my eyes. Yet I need to have something for my portfolio, so here we are 😂

The app mainly uses Flask, Bootstrap, HTML and CSS.

## Function 
AKB48World is a typical, boring mobile game: you have cards in your hands, and each level has a target score. You need to figure out what is the best team to pass the level. 

The pain point of the game is it has different weighting of each attributes on the levels, and the game does not show the best cards option by their UI. You have to choose your cards completely by your own. 
<details>
<summary>Here is the sample of a card: </summary>

<img src="https://github.com/nicolelaitc/AKB48WorldCalc/assets/92098962/9b4ea9c5-4da8-4e26-b506-545b6e72a634" height="400" />
  
```
{'theme': '#今日のコーデ', 'team': 'K', 'member': '込山榛香', 'singing': 805, 'dancing': 18601.44, 'variety': 5876, 'style': 942, 'skill_type': 'dancing', 'skill_target': 'Herself', 'skill_rate': 43.0, 'cheer': '小栗有以', 'cheer_skill': 'style', 'cheer_rate': 10.0, 'total': 8214}
```

</details>
Each attributes in the data has some effects towards the final score of the level. 


The calculator can
- saving cards details for simulation
- calculating the cards you should use for each level
- create custom member/theme to adapt the future release of new cards (since I cannot even find the card list of this game 😂)

## Future update 
I expect I will update this app by completely remove the SQL database annd login/logout mechanism and let users import/export data instead.

## License 
MIT

## Credit
I made it alone (with the help of ChatGPT) 
### Inspiration 
https://fgosim.github.io/Material/ -> It is a really great calculator-type of things for mobile game




