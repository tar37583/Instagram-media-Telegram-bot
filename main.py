import os
import instaloader
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

# Define your keyboard
main_keyboard = [
    ['ℹ Help', '💰 Donate']
]

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        '👋 Welcome to my bot! It can download any type of media on Instagram! (Public accounts only)',
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
    )

async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Send an Instagram link for a PUBLIC Post, Video, IGTV or Reel to download it! Stories are not currently supported.\n\n'
        'To download a user profile image, just send its username',
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
    )

async def donate(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Thank you for donating! ❤\n\nThis will help covering the costs of the hosting',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        'Buy Me A Coffee', url='https://www.buymeacoffee.com/simonfarah'
                    )
                ]
            ]
        ),
    )

def download_instagram_media(url: str):
    L = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(L.context, url.split('/')[-2])
    
    if post.is_video:
        L.download_post(post, target='downloads')
        return post.video_url, "video"
    elif post.typename == 'GraphImage':
        L.download_post(post, target='downloads')
        return post.url, "photo"
    elif post.typename == 'GraphSidecar':
        L.download_post(post, target='downloads')
        return [node.video_url if node.is_video else node.display_url for node in post.get_sidecar_nodes()], "sidecar"
    else:
        return None, None

async def send_post(update: Update, context: CallbackContext):
    url = update.message.text

    media_url, media_type = download_instagram_media(url)

    if media_type == "video":
        await update.message.reply_video(media_url)
    elif media_type == "photo":
        await update.message.reply_photo(media_url)
    elif media_type == "sidecar":
        for media in media_url:
            if "video" in media:
                await update.message.reply_video(media)
            else:
                await update.message.reply_photo(media)
    else:
        await update.message.reply_text('Send Me Only Public Instagram Posts')

async def send_dp(update: Update, context: CallbackContext):
    username = update.message.text.strip()
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)

    await update.message.reply_photo(profile.profile_pic_url)

def main():
    BOT_TOKEN = 'YOUR_TOKEN'
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex('Help'), help))
    application.add_handler(MessageHandler(filters.Regex('Donate'), donate))
    application.add_handler(MessageHandler(filters.Regex('http') & filters.Regex('instagram'), send_post))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_dp))

    application.run_polling()

if __name__ == '__main__':
    print('Bot is running...')
    main()
