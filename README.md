# adminbot

adminbot is a silly, but useful, bot designed to automatically moderate the moderators of a Discord server and to shame them when they have abused their moderator powers, i.e. removing the ability to speak for certain users. The main function is to unban, invite and give roles to abused users who have been unfairly admin abused on the server. To shame the admins, it keeps a daily tally of the number of admin abuses throughout the day. However, it also features a handful of silly functions including a Markov Chain chatbot which responds randomly to user’s messages, gradually learning how to speak (mostly nonsense) from the users it interacts with.

## Commands

```
A very stupid Discord bot which can do auto-moderation

Admin Abuse:
  abuse   Check the audit logs for abuses against the user within the last x ...
  invite  Invite the user to the server via DM. This can be called in another
  last    Check the audit log for the last incident including the user as the
  mission Send a message to the channel to say what the point of this bot is.
  roles   Update the roles so the user is a Cunt and a Cunts and/or Lads.
  unban   Unban the user from the server and re-invite.
Spambot:
  badword Speak a bad word into the chat. If a certain bad word is said, then
  chat    Generates a random sentence using the Markov Chain chat bot trained
  learn   Force the MC bot to update its Markov Chain to learn new phrases.
  oracle  Send a message from the temple from God (Terry Davis/the Oracle).
Utility:
  picture Send a link to a picture in the channel. This will only work 0.001% of
​No Category:
  help    Shows this message

Type %help command for more info on a command.
You can also type %help category for more info on a category.
```
