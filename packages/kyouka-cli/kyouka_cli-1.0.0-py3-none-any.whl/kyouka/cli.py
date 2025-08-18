#!/usr/bin/env python
import os
import yt_dlp
import pygame
import argparse
import time
import threading
import random
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

VIDEOS_DIR = "videos"
APP_NAME = "Kyouka"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71'
]

def get_terminal_size():
    try:
        return os.get_terminal_size()
    except OSError:
        return 80, 24

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_videos_dir():
    if not os.path.exists(VIDEOS_DIR):
        os.makedirs(VIDEOS_DIR)

def display_title():
    clear_screen()
    title = f"""

██╗░░██╗██╗░░░██╗░█████╗░██╗░░░██╗██╗░░██╗░█████╗
██║░██╔╝╚██╗░██╔╝██╔══██╗██║░░░██║██║░██╔╝██╔══██╗
█████═╝░░╚████╔╝░██║░░██║██║░░░██║█████═╝░███████║
██╔═██╗░░░╚██╔╝░░██║░░██║██║░░░██║██╔═██╗░██╔══██║
██║░╚██╗░░░██║░░░╚█████╔╝╚██████╔╝██║░╚██╗██║░░██║
╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝

                        
"""
    print(title)

def download_media(url, audio_only=False):
    clear_screen()
  
    user_agent = random.choice(USER_AGENTS)
    
    ydl_opts = {
        'outtmpl': os.path.join(VIDEOS_DIR, '%(title)s.%(ext)s'),
        'sleep_interval': 5,  
        'retries': 10,  
        'user_agent': user_agent,
        'cookiefile': 'cookies.txt',
        'ignoreerrors': True,
    }
    if audio_only:
        # Audio download configuration
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320', 
        }]
        expected_ext = '.mp3'
    else:
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        expected_ext = '.mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            base_filename = ydl.prepare_filename(info_dict)
            base = os.path.splitext(base_filename)[0]
            final_filename = base + expected_ext

         
            ydl.download([url])
            
           
            if os.path.exists(final_filename):
                print(f"Media saved as: {os.path.basename(final_filename)}")
            else:
                actual_files = [f for f in os.listdir(VIDEOS_DIR) if f.startswith(os.path.basename(base))]
                if actual_files:
                    print(f"Media saved as: {actual_files[0]}")
                else:
                    print("Media downloaded but the final file could not be determined.")
            
        print("Media downloaded successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    input("Press Enter to continue...")

def list_media():
    clear_screen()
    print("--- Downloaded Media ---")
    if not os.path.exists(VIDEOS_DIR):
        print("No media found.")
        return []
    media = os.listdir(VIDEOS_DIR)
    if not media:
        print("No media found.")
    else:
        for i, item in enumerate(media):
            print(f"{i+1}. {item}")
    return media

class MediaPlayer:
    def __init__(self, audio_only=False):
        if not VLC_AVAILABLE:
            raise ImportError("VLC is required for this player. Install with: pip install python-vlc")
        
        vlc_args = [
            '--intf', 'dummy', 
            '--no-video-title-show', 
            '--quiet',
        ]
        
        if os.name == 'nt':  
            vlc_args.extend(['--vout', 'direct3d11', '--aout', 'directsound'])
        else: 
            vlc_args.extend(['--vout', 'x11,xcb', '--aout', 'alsa'])
        
        if audio_only:
            vlc_args.extend(['--no-video'])
        
        try:
            self.instance = vlc.Instance(vlc_args)
            self.player = self.instance.media_player_new()
            self.is_playing = False
            self.current_media = None
            self.player_name = f"{APP_NAME} Player"
        except Exception as e:
            print(f"Warning: Could not initialize player: {e}")
            self.instance = vlc.Instance(['--intf', 'dummy'])
            self.player = self.instance.media_player_new()
            self.is_playing = False
            self.current_media = None
        
    def play_media(self, file_path):
        """Play media with our player"""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
            
        try:
            media = self.instance.media_new(file_path)
            self.player.set_media(media)
            self.current_media = media
            
            print(f"Starting {self.player_name}...")
            ret = self.player.play()
            if ret == -1:
                print("Error: Could not start playback")
                return          
            self.is_playing = True            
            time.sleep(1.5)
            
 
            state = self.player.get_state()
            if state == vlc.State.Error:
                print("Error: Player encountered an error")
                print("The file might be corrupted or in an unsupported format")
                return
            elif state == vlc.State.Ended:
                print("The media file appears to be empty or very short")
                return
            
         
            self.show_controls()
            self.playback_loop()
            
        except Exception as e:
            print(f"Error playing media: {e}")
            print("Try using a different player")
    
    def show_controls(self):
        """Display playback controls"""
        print("\n" + "="*50)
        print(f"{self.player_name} CONTROLS:")
        print("Press Ctrl+C to stop playback")
        print("Close player window to return to menu")
        print("="*50)
        print("Note: Player controls may vary by platform")
        print("="*50)
        
    def playback_loop(self):
        """Handle playback control loop"""
        try:
            while self.is_playing:
                if not VLC_AVAILABLE:
                    break
                    
                state = self.player.get_state()
                
                if state == vlc.State.Ended:
                    print("\nPlayback finished.")
                    break
                elif state == vlc.State.Error:
                    print("\nPlayback error occurred.")
                    break
                elif state == vlc.State.Stopped:
                    print("\nPlayback stopped.")
                    break
                
    
                current_time = max(0, self.player.get_time() // 1000)  
                duration = max(0, self.player.get_length() // 1000)
                
                if duration > 0 and current_time >= 0:
                    progress = min(100, (current_time / duration) * 100)
                    print(f"\rTime: {self.format_time(current_time)}/{self.format_time(duration)} [{progress:.1f}%] | Press Ctrl+C to stop", end="", flush=True)
                else:
                    print(f"\rPlaying... Press Ctrl+C to stop", end="", flush=True)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nPlayback stopped by user.")
        finally:
            self.stop()
    
    def format_time(self, seconds):
        """Format time in MM:SS format"""
        if seconds < 0:
            return "00:00"
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def stop(self):
        """Stop playback"""
        if self.player:
            self.player.stop()
        self.is_playing = False

def builtin_video_player(file_path):
    """Built-in video player without audio"""
    if not CV2_AVAILABLE or not TKINTER_AVAILABLE:
        print("Missing dependencies. Install with: pip install opencv-python pillow")
        return
        
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print("Error: Could not open video file")
            return
            
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_delay = int(1000 / fps)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"Starting {APP_NAME} Built-in Video Player (no audio)...")
        print(f"Video: {fps:.1f} FPS, {duration:.1f}s duration")
        
        root = tk.Tk()
        root.title(f"{APP_NAME} Video Player")
        
      
        playing = [True]
        current_frame = [0]
        should_close = [False]  
        
        def close_window():
            """Handle window closing"""
            playing[0] = False
            should_close[0] = True
            try:
                cap.release()
                root.quit()
                root.destroy()
            except:
                pass
        root.protocol("WM_DELETE_WINDOW", close_window)
        video_label = tk.Label(root)
        video_label.pack()
        
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def toggle_play_pause():
            playing[0] = not playing[0]
            play_button.config(text="Play" if not playing[0] else "Pause")
        
        def seek_backward():
            current_frame[0] = max(0, current_frame[0] - int(fps * 10)) 
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame[0])
        
        def seek_forward():
            current_frame[0] = min(total_frames - 1, current_frame[0] + int(fps * 10)) 
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame[0])
        
        def close_player():
            """Close button handler"""
            close_window()
        tk.Button(control_frame, text="<<10s", command=seek_backward).pack(side=tk.LEFT)
        play_button = tk.Button(control_frame, text="Pause", command=toggle_play_pause)
        play_button.pack(side=tk.LEFT)
        tk.Button(control_frame, text="10s>>", command=seek_forward).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Close", command=close_player, bg="red", fg="white").pack(side=tk.LEFT, padx=(20,0))
        
        progress_label = tk.Label(control_frame, text="00:00 / 00:00")
        progress_label.pack(side=tk.RIGHT)
        
        def update_frame():
            """Update video frame"""
            try:
                if should_close[0]:
                    return 
                    
                if not playing[0]:
                    if not should_close[0]:
                        root.after(50, update_frame)
                    return
                
                ret, frame = cap.read()
                if not ret:
                    print("Video finished")
                    close_window()
                    return
                
                current_frame[0] += 1
                current_time = current_frame[0] / fps
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = frame_rgb.shape[:2]
                max_width, max_height = 800, 600
                
                if width > max_width or height > max_height:
                    scale = min(max_width/width, max_height/height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
                pil_image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(pil_image)                
                if not should_close[0] and video_label.winfo_exists():
                    video_label.configure(image=photo)
                    video_label.image = photo  
                    
                    progress_text = f"{int(current_time//60):02d}:{int(current_time%60):02d} / {int(duration//60):02d}:{int(duration%60):02d}"
                    progress_label.config(text=progress_text)
                if not should_close[0]:
                    try:
                        root.after(frame_delay, update_frame)
                    except tk.TclError:
                        should_close[0] = True
                        
            except (tk.TclError, AttributeError):
                should_close[0] = True
            except Exception as e:
                print(f"Error updating frame: {e}")
                close_window()
        
        print("Close the video window or click 'Close' button to return to menu")
        root.bind('<Escape>', lambda e: close_window())  
        root.after(100, update_frame) 
        try:
            root.mainloop()
        except:
            pass
        finally:
            try:
                cap.release()
                if root.winfo_exists():
                    root.destroy()
            except:
                pass
        
        print("Player closed, returning to menu...")
        
    except Exception as e:
        print(f"Error in video player: {e}")

def audio_player_no_video(file_path):
    """Audio player without video"""
    if not VLC_AVAILABLE:
        print("VLC is required for this player. Install with: pip install python-vlc")
        return
        
    try:
        player = MediaPlayer(audio_only=True)
        player.player_name = f"{APP_NAME} Audio Player"
        player.play_media(file_path)
    except Exception as e:
        print(f"Error playing audio: {e}")

def play_media_cli():
    media = list_media()
    if not media:
        input("Press Enter to continue...")
        return
    
    try:
        choice = int(input("Choose a media to play: ")) - 1
        if 0 <= choice < len(media):
            file_path = os.path.join(VIDEOS_DIR, media[choice])
            file_ext = os.path.splitext(file_path)[1].lower()
            
            print("\nChoose playback mode:")
            available_options = []
            
            if file_ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
                if VLC_AVAILABLE:
                    option_num = len(available_options) + 1
                    print(f"{option_num}. Player (Audio and Video - Recommended)")
                    available_options.append((str(option_num), "av_player"))
              
                if TKINTER_AVAILABLE and CV2_AVAILABLE:
                    option_num = len(available_options) + 1
                    print(f"{option_num}. Built-in Video Player (no audio)")
                    available_options.append((str(option_num), "video_only"))
                
                if VLC_AVAILABLE:
                    option_num = len(available_options) + 1
                    print(f"{option_num}. Audio Player (no video)")
                    available_options.append((str(option_num), "audio_only"))
              
            elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                if VLC_AVAILABLE:
                    option_num = len(available_options) + 1
                    print(f"{option_num}. Audio Player (no video)")
                    available_options.append((str(option_num), "audio_only"))
                
                option_num = len(available_options) + 1
                print(f"{option_num}. Built-in Audio Player")
                available_options.append((str(option_num), "builtin_audio"))
                
            else:
                print("Unsupported file type. Trying fallback player...")
                if VLC_AVAILABLE:
                    print("1. Player (Audio and Video - Recommended)")
                    available_options.append(("1", "av_player"))
            
            if not available_options:
                print("No compatible players available for this file format")
                input("Press Enter to continue...")
                return
            
            mode_choice = input(f"Enter your choice (1-{len(available_options)}): ").strip()
          
            selected_mode = None
            for option, mode in available_options:
                if option == mode_choice:
                    selected_mode = mode
                    break
            
            if selected_mode == "av_player":
                player = MediaPlayer(audio_only=False)
                player.play_media(file_path)
            elif selected_mode == "video_only":
                builtin_video_player(file_path)
            elif selected_mode == "audio_only":
                audio_player_no_video(file_path)
            else:
                print("Invalid choice.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    input("\nPress Enter to continue...")

def rename_media():
    media = list_media()
    if not media:
        input("Press Enter to continue...")
        return

    try:
        choice = int(input("Choose a media to rename: ")) - 1
        if 0 <= choice < len(media):
            old_path = os.path.join(VIDEOS_DIR, media[choice])
            new_name = input("Enter the new name (with extension): ").strip()
            if new_name:
                new_path = os.path.join(VIDEOS_DIR, new_name)
                os.rename(old_path, new_path)
                print("Media renamed successfully!")
            else:
                print("Invalid name.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"Error renaming file: {e}")
    
    input("Press Enter to continue...")

def delete_media():
    media = list_media()
    if not media:
        input("Press Enter to continue...")
        return
    
    try:
        choice = int(input("Choose a media to delete: ")) - 1
        if 0 <= choice < len(media):
            file_path = os.path.join(VIDEOS_DIR, media[choice])
            confirm = input(f"Are you sure you want to delete '{media[choice]}'? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                os.remove(file_path)
                print("Media deleted successfully!")
            else:
                print("Deletion cancelled.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    input("Press Enter to continue...")

def display_menu():
    display_title()
    print("1. Download media")
    print("2. List media")
    print("3. Play media")
    print("4. Rename media")
    print("5. Delete media")
    print("6. Exit")
    if not VLC_AVAILABLE and not CV2_AVAILABLE:
        print(f"\nNote: Install dependencies for full features:")
        print("pip install python-vlc opencv-python")
    return input("Choose an option: ").strip()

def run_cli():
    """Main entry point that runs the CLI interface"""
    create_videos_dir()
    
    try:
        while True:
            choice = display_menu()
            if choice == '1':
                url = input("Enter the video URL: ").strip()
                if url:
                    download_media(url)
                else:
                    print("Invalid URL.")
                    input("Press Enter to continue...")
            elif choice == '2':
                list_media()
                input("Press Enter to continue...")
            elif choice == '3':
                play_media_cli()
            elif choice == '4':
                rename_media()
            elif choice == '5':
                delete_media()
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - Video Downloader and Player")
    parser.add_argument('-d', '--download', type=str, help="Download a video from a URL")
    parser.add_argument('-da', '--download_audio', type=str, help="Download audio only from a URL")
    parser.add_argument('-l', '--list', action='store_true', help="List downloaded media")
    parser.add_argument('-p', '--play', type=str, help="Play a downloaded media file")
    parser.add_argument('-r', '--rename', nargs=2, metavar=('OLD_NAME', 'NEW_NAME'), help="Rename a media file")
    parser.add_argument('-del', '--delete', type=str, metavar='FILE_NAME', help="Delete a media file")
    parser.add_argument('--cli', action='store_true', help="Run in CLI mode")

    args = parser.parse_args()

    if not any(vars(args).values()):
        run_cli()
        return

    create_videos_dir()
    
    if args.download:
        download_media(args.download)
    elif args.download_audio:
        download_media(args.download_audio, audio_only=True)
    elif args.list:
        list_media()
    elif args.play:
        file_path = os.path.join(VIDEOS_DIR, args.play)
        if os.path.exists(file_path):
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
                if VLC_AVAILABLE:
                    player = MediaPlayer(audio_only=False)
                    player.play_media(file_path)
                else:
                    print("VLC not available. Using built-in player...")
                    builtin_video_player(file_path)
            elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                audio_player_no_video(file_path)
            else:
                print("Unsupported file format")
        else:
            print(f"File not found: {args.play}")
    elif args.rename:
        old_path = os.path.join(VIDEOS_DIR, args.rename[0])
        new_path = os.path.join(VIDEOS_DIR, args.rename[1])
        if os.path.exists(old_path):
            try:
                os.rename(old_path, new_path)
                print(f"Renamed {args.rename[0]} to {args.rename[1]}")
            except Exception as e:
                print(f"Error renaming file: {e}")
        else:
            print(f"File not found: {args.rename[0]}")
    elif args.delete:
        file_path = os.path.join(VIDEOS_DIR, args.delete)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted {args.delete}")
            except Exception as e:
                print(f"Error deleting file: {e}")
        else:
            print(f"File not found: {args.delete}")
    elif args.cli:
        run_cli()

if __name__ == "__main__":
    main()