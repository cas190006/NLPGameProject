# NLPGameProject

For our NLP course project, we have created a simple text-based game that utilizes NLP. In this game, players face a variety of scenarios while trying to escape a dungeon and the only way to overcome these scenarios is choosing appropriate actions through textual inputs.

The NLP concepts used are a player input parser and text message generator. When a player inputs their desired command, the parser breaks the command into its action and direct/indirect objects. Given the current state of the game and the desired action onto the requested direct/indirect object, it performs that action unless it can’t be done onto that object or at this time. When it performs a valid action, it is reflected in the game and the text generated in response.

The text generator is a simple language model using the concept of ngrams. The n value for these ngrams varies between 3 and 6 depending on the purpose of the text generated. The data that the text generator uses is located in the textGeneratorData.txt file. 

When you run the game, make sure that the textGeneratorData.txt file is in the same directory as the game file.
