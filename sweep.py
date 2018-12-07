import lib.controller.CommandHandler as CommandHandler
import lib.controller.BannerController


if __name__ == '__main__':
    lib.controller.BannerController.BannerLoader().ShowBanner()
    Handler = CommandHandler.CommandHandler()
    Handler._GetCommand()
    pass