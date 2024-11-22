import React, { useState } from 'react';
import {
  ConversationHeader,
  Avatar,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
  Button,
} from '@chatscope/chat-ui-kit-react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import logo from '../assets/robotnew.png';
import agent from '../assets/robotface.png';

function ChatComponent({ token, onLogout }) {
  const [messages, setMessages] = useState([
    {
      message:
        'Hello, and welcome to Shopwise Solutions! Let me know how I can help you',
      direction: 'incoming',
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = async (messageText) => {
    addMessageToChat({ text: messageText, direction: 'outgoing' });

    try {
      // Show typing indicator
      setIsTyping(true);
      let partialResponse = '';
      const ws = new WebSocket('wss://shop.migage.com/ws/chat');
      console.log('websocket');
      ws.onopen = () => {
        console.log('websocket is open');
        // Send message payload with token
        ws.send(
          JSON.stringify({
            token,
            chatMessage: messageText,
          })
        );
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
        if (data.error) {
          addMessageToChat({ text: data.error, direction: 'incoming' });
        } else {
          partialResponse += data.response;

          if (data.isCompleted) {
            addMessageToChatTyping({
              text: partialResponse + data.response,
              direction: 'incoming',
            });
            setIsTyping(false);
          } else {
            addMessageToChatTyping({
              text: partialResponse,
              direction: 'incoming',
            });
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addMessageToChat({
          text: 'Sorry, something went wrong. Please try again. If error persists then re-login by refreshing the Page.',
          direction: 'incoming',
        });
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed.');
        addMessageToChat({
          text: 'Looks like the session has ended. Please refresh and Login again.',
          direction: 'incoming',
        });
        setIsTyping(false);
      };
    } catch (error) {
      console.error('Failed to send message:', error);
      addMessageToChat({
        text: 'Failed to send message.',
        direction: 'incoming',
      });
    } finally {
      // Hide typing indicator
      console.log('finally');
      // setIsTyping(false);
    }
  };

  const addMessageToChat = (newMessage) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { message: newMessage.text, direction: newMessage.direction },
    ]);
  };

  const addMessageToChatTyping = (message) => {
    setMessages((prevMessages) => {
      let newMessage = [];
      if (
        prevMessages.length > 0 &&
        prevMessages[prevMessages.length - 1].direction === 'incoming'
      ) {
        const msgs = prevMessages.slice(0, -1);
        newMessage = [
          ...msgs,
          { message: message.text, direction: message.direction },
        ];
        return newMessage;
      }

      newMessage = [
        ...prevMessages,
        { message: message.text, direction: message.direction },
      ];
      console.log('Updated Messages: ', newMessage);
      return newMessage;
    });
  };

  const handleLogout = () => {
    // Clear the token or session data
    localStorage.removeItem('token');
    if (onLogout) {
      onLogout(); // Trigger parent logout handler to redirect or reset app state
    }
  };

  return (
    <ChatContainer>
      <ConversationHeader>
        <Avatar name="Connected Ai" status="available" src={logo} />
        <ConversationHeader.Content info="Active" userName="Connected Ai" />
        <ConversationHeader.Actions>
          <Button
            style={{
              backgroundColor: '#467D7A', // Primary color for the button
              color: '#F9FBFF', // White color for text
              border: 'none',
              padding: '5px 10px',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
            onClick={handleLogout}
          >
            Logout
          </Button>
        </ConversationHeader.Actions>
      </ConversationHeader>
      <MessageList
        typingIndicator={
          isTyping && <TypingIndicator content="Connected Ai is typing..." />
        }
      >
        {messages.map((msg, index) => (
          <Message
            key={index}
            model={{
              message: msg.message,
              sentTime: 'just now',
              direction: msg.direction,
              position: 'single',
            }}
          >
            {msg.direction === 'incoming' ? (
              <Avatar name="Connected Ai" src={agent} />
            ) : (
              ''
            )}
          </Message>
        ))}
      </MessageList>
      <MessageInput
        attachButton={false}
        sendDisabled={isTyping}
        placeholder="Type a message..."
        onSend={handleSendMessage}
      />
    </ChatContainer>
  );
}

export default ChatComponent;
